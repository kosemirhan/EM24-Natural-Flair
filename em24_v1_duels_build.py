#!/usr/bin/env python3
"""EM24 Natural Flair v1.1 Duels: applies an experimental, moderately more physical contact profile.

Requires Python 3.9+ and zstandard (pip install zstandard).
Leaves source untouched. Public script contains no game files; input must be an owned FM24 file.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
try:
    import zstandard as zstd
except ImportError:
    zstd = None
import ctypes
import ctypes.util

class Compression:
    def __init__(self):
        self.zstd = zstd
        if self.zstd is None:
            libname = ctypes.util.find_library('zstd')
            if not libname:
                raise RuntimeError('zstandard is required. Run: pip install zstandard')
            self.lib = ctypes.CDLL(libname)
            self.lib.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
            self.lib.ZSTD_decompress.restype = ctypes.c_size_t
            self.lib.ZSTD_compress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
            self.lib.ZSTD_compress.restype = ctypes.c_size_t
            self.lib.ZSTD_compressBound.argtypes = [ctypes.c_size_t]
            self.lib.ZSTD_compressBound.restype = ctypes.c_size_t
            self.lib.ZSTD_getFrameContentSize.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
            self.lib.ZSTD_getFrameContentSize.restype = ctypes.c_ulonglong
            self.lib.ZSTD_isError.argtypes = [ctypes.c_size_t]
            self.lib.ZSTD_isError.restype = ctypes.c_uint

    def decompress(self, frame: bytes) -> bytes:
        if self.zstd is not None:
            return self.zstd.ZstdDecompressor().decompress(frame, max_output_size=20_000_000)
        buf = ctypes.create_string_buffer(frame)
        n = self.lib.ZSTD_getFrameContentSize(buf, len(frame))
        if n > 20_000_000:
            raise ValueError('Invalid or excessively large zstd frame')
        dst = ctypes.create_string_buffer(n)
        res = self.lib.ZSTD_decompress(dst, n, buf, len(frame))
        if self.lib.ZSTD_isError(res):
            raise ValueError('zstd decompression failed')
        return dst.raw[:res]

    def compress(self, content: bytes, level: int = 6) -> bytes:
        if self.zstd is not None:
            return self.zstd.ZstdCompressor(level=level).compress(content)
        src = ctypes.create_string_buffer(content)
        cap = self.lib.ZSTD_compressBound(len(content))
        dst = ctypes.create_string_buffer(cap)
        res = self.lib.ZSTD_compress(dst, cap, src, len(content), level)
        if self.lib.ZSTD_isError(res):
            raise ValueError('zstd compression failed')
        return dst.raw[:res]

# Experimental v1.0 physics profile. Both known physics variants are patched.
# Each integer is a global physics threshold, NOT an animation/AI probability.
# Only three verified source physics versions are accepted: original, EM24 v0.1 and EM24 v1.0.
ALLOWED_INPUT_PHYSICS_SHA256 = {
    'fa8a7ef5d7fbb2e14ffa5879fa07c44603f1a14d7b95b651dace84cb2a98afd0': 'original FM24 sample',
    '40be47cc9f8bfee155b9afed933e278946810404f088e9071966819b646d7edd': 'EM24 Natural Flair v0.1',
    '78dd5a72c81fd9c436b958525d4e1566dd2d83e13438938b0d77f4931cf734f8': 'EM24 Natural Flair v1.0',
}
PATCH_GROUPS = {
    'movement': {
        'theoretical_max_acceleration': (91900, 91900),
        'theoretical_max_deceleration': (46300, 46300),
        'theoretical_max_turning_rate': (186, 186),
        'theoretical_max_potential_direction_change_jog': (109, 109),
        'theoretical_max_potential_direction_change_run': (56, 56),
    },
    'ball_and_finishing': {
        'soft_kick_speed': (49000, 49000),
        'soft_to_medium_kick_speed': (89000, 89000),
        'medium_kick_speed': (126500, 165500),
        'medium_to_moderate_kick_speed': (176000, 206000),
        'moderate_kick_speed': (218000, 248000),
        'quite_hard_kick_speed': (268500, 288500),
        'hard_kick_speed': (308000, 328000),
        'basic_header_speed': (121000, 131000),
    },
    'contact_and_second_balls': {
        # Moderate adjustment to minimum action and post-contact intervals, not foul probabilities.
        'min_delay_for_ball_lunge_do': (1460, 1460),
        'min_delay_for_ball_lunge_receive': (790, 790),
        'min_delay_for_block_tackle_do': (470, 470),
        'min_delay_for_block_tackle_receive': (800, 800),
        'min_delay_for_deflect_ball_receive': (515, 515),
        'min_delay_for_force_opponent_to_lose_ball_do': (470, 470),
        'min_delay_for_force_opponent_to_lose_ball_receive': (525, 525),
        'min_delay_for_shoulder_charge_do': (470, 470),
        'min_delay_for_shoulder_charge_receive': (2130, 2130),
        'min_delay_for_slide_tackle_do': (1450, 1450),
        'min_delay_for_slide_tackle_receive': (815, 815),
    },
    'goalkeeper': {
        'theoretical_max_diving_acceleration': (90000, 90000),
        'theoretical_max_diving_speed': (75750, 75750),
        'min_delay_keeper_save_dive_but_not_held': (780, 780),
        'min_delay_keeper_save_no_dive_not_held': (520, 520),
    },
}
PATCHES = {k: val for group in PATCH_GROUPS.values() for k, val in group.items()}
assert len(PATCHES) == sum(len(x) for x in PATCH_GROUPS.values())

MAGIC = b'\x02\x01fmf.\x08\x00\x00'
BLOCK_MAGIC = b'\x28\xb5\x2f\xfd'
ROOT_OFFSET = 26
PHYSICS_PATH = 'simatch/physics/physical_constraints.jsb'

def parse_index(index: bytes):
    """Parse FM24's nested file directory table, recording writable metadata slots."""
    pos = 0
    entries = []
    def read_string():
        nonlocal pos
        if pos + 4 > len(index): raise ValueError('Truncated index string length')
        count = struct.unpack_from('<I', index, pos)[0]
        pos += 4
        if count > 1024 or pos + count > len(index): raise ValueError('Unexpected index string')
        value = index[pos:pos + count].decode('utf8')
        pos += count
        return value
    def read_dir(parent='', depth=0):
        nonlocal pos
        if depth > 16: raise ValueError('Excessive directory depth')
        path = (parent + '/' if parent else '') + read_string()
        n_files = struct.unpack_from('<I', index, pos)[0]
        pos += 4
        if n_files > 10_000: raise ValueError('Unreasonable file count')
        for _ in range(n_files):
            basename, extension = read_string(), read_string()
            if pos + 40 > len(index):raise ValueError('Truncated file metadata')
            metadata_position = pos
            off, packed, raw, t1, t2 = struct.unpack_from('<5Q',index,pos)
            pos += 40
            entries.append({'path':path+'/'+basename+extension,'meta_at':metadata_position,
                           'offset':off,'packed':packed,'raw':raw,'times':(t1,t2)})
        n_dirs = struct.unpack_from('<I',index,pos)[0]
        pos += 4
        if n_dirs > 1000:raise ValueError('Unreasonable directory count')
        for _ in range(n_dirs):read_dir(path,depth+1)
    read_dir()
    if pos != len(index):raise ValueError(f'Unparsed index bytes: {len(index)-pos}')
    return entries

def unpack_blocks(compressed_section: bytes, compressor: Compression) -> bytes:
    pos=0
    out=bytearray()
    while pos < len(compressed_section):
        if pos+8>len(compressed_section):raise ValueError('Incomplete zstd block header')
        size=struct.unpack_from('<I',compressed_section,pos)[0]
        pos+=4
        if size < 8 or compressed_section[pos:pos+4]!=BLOCK_MAGIC or pos+size>len(compressed_section):
            raise ValueError('Invalid FMF compressed block')
        out.extend(compressor.decompress(compressed_section[pos:pos+size]))
        pos+=size
    return bytes(out)

def get_archive_parts(blob: bytes, compressor: Compression):
    if not blob.startswith(MAGIC) or len(blob)<64:raise ValueError('Not a supported FM24 FMF archive')
    trailing_header=struct.unpack_from('<Q',blob,9)[0]+9
    if trailing_header >= len(blob) or blob[trailing_header:trailing_header+9]!=MAGIC:
        raise ValueError('Missing FMF directory footer or incompatible archive version')
    index_packed_size=struct.unpack_from('<I',blob,trailing_header+9)[0]
    index_frame=blob[trailing_header+13:trailing_header+13+index_packed_size]
    if len(index_frame)!=index_packed_size or trailing_header+13+index_packed_size!=len(blob):
        raise ValueError('Unexpected footer layout')
    index_data=compressor.decompress(index_frame)
    entries=parse_index(index_data)
    return trailing_header,index_data,entries

def extract(blob: bytes, entry: dict, compressor: Compression):
    s=ROOT_OFFSET+entry['offset']; e=s+entry['packed']
    return unpack_blocks(blob[s:e],compressor)

def patch_jsb(jsb: bytes):
    output=bytearray(jsb)
    diff={}
    for key, expected_new in PATCHES.items():
        kb=bytes([len(key)])+key.encode('ascii')
        matches=list(re.finditer(re.escape(kb),jsb))
        if len(matches)!=len(expected_new):
            raise ValueError(f'Cannot patch {key}: expected {len(expected_new)} occurrences, got {len(matches)}')
        previous=[]
        for i,match in enumerate(matches):
            tag_pos=match.end()
            if jsb[tag_pos]!=2:raise ValueError(f'Unexpected type tag for {key}')
            position=tag_pos+1
            original=struct.unpack_from('<i',jsb,position)[0]
            previous.append(original)
            struct.pack_into('<i',output,position,expected_new[i])
        diff[key]={'before':previous,'after':list(expected_new)}
    if len(output)!=len(jsb):raise AssertionError('Patch cannot alter JSB size')
    return bytes(output),diff

def build(source: Path, output: Path, jsb_output: Path, report_output: Path):
    compressor=Compression()
    blob=source.read_bytes()
    footer_begin,index,entries=get_archive_parts(blob,compressor)
    found=[e for e in entries if e['path']==PHYSICS_PATH]
    if len(found)!=1:raise ValueError('Could not identify exactly one physics file')
    original_entry=found[0]
    original_jsb=extract(blob,original_entry,compressor)
    source_physics_sha256 = hashlib.sha256(original_jsb).hexdigest()
    if source_physics_sha256 not in ALLOWED_INPUT_PHYSICS_SHA256:
        raise ValueError('Unknown or previously modded simatch.fmf: original physics SHA-256 not recognized; restore a supported original, EM24 v0.1 or v1.0 file first')
    if len(original_jsb)!=original_entry['raw']:
        raise ValueError('Physics file failed size verification')
    modified_jsb,diff=patch_jsb(original_jsb)
    # Check the v1.1 values for a physically monotonically increasing kick-speed ladder.
    kicks = ['soft_kick_speed', 'soft_to_medium_kick_speed', 'medium_kick_speed',
             'medium_to_moderate_kick_speed', 'moderate_kick_speed',
             'quite_hard_kick_speed', 'hard_kick_speed']
    for profile in range(2):
        kick_series = [PATCHES[key][profile] for key in kicks]
        if kick_series != sorted(kick_series) or len(kick_series)!=len(set(kick_series)):
            raise AssertionError('Non-monotonic kick-speed ladder for profile '+str(profile))
    packed_frame=compressor.compress(modified_jsb)
    new_block=struct.pack('<I',len(packed_frame))+packed_frame
    delta=len(new_block)-original_entry['packed']
    new_index=bytearray(index)
    changed_offsets=0
    for entry in entries:
        if entry['path']==PHYSICS_PATH:
            struct.pack_into('<Q',new_index,entry['meta_at']+8,len(new_block))
        elif entry['offset']>original_entry['offset']:
            struct.pack_into('<Q',new_index,entry['meta_at'],entry['offset']+delta)
            changed_offsets+=1
    orig_start=ROOT_OFFSET+original_entry['offset']
    orig_end=orig_start+original_entry['packed']
    prefix=bytearray(blob[:orig_start])
    struct.pack_into('<Q',prefix,9,footer_begin+delta-9)
    new_index_frame=compressor.compress(bytes(new_index))
    result=(bytes(prefix)+new_block+blob[orig_end:footer_begin]+MAGIC+
           struct.pack('<I',len(new_index_frame))+new_index_frame)
    # Re-parse new archive and compare every original resource independently.
    new_footer_begin,new_index_decoded,new_entries=get_archive_parts(result,compressor)
    new_by_name={e['path']:e for e in new_entries}
    original_by_name={e['path']:e for e in entries}
    if len(new_entries)!=len(entries):raise AssertionError('File listing changed unexpectedly')
    for name,entry in original_by_name.items():
        old_raw=extract(blob,entry,compressor)
        new_raw=extract(result,new_by_name[name],compressor)
        if name==PHYSICS_PATH:
            if new_raw!=modified_jsb:raise AssertionError('Modified physics mismatch')
        elif old_raw!=new_raw:
            raise AssertionError('Unexpected change in '+name)
    if new_footer_begin!=footer_begin+delta:raise AssertionError('Archive footer offset mismatch')
    if source.resolve() == output.resolve():
        raise ValueError('Output may not overwrite the original game file')
    output.write_bytes(result)
    jsb_output.write_bytes(modified_jsb)
    report={'source':source.name,'source_sha256':hashlib.sha256(blob).hexdigest(),
            'output':output.name,'output_sha256':hashlib.sha256(result).hexdigest(),
            'source_size':len(blob),'result_size':len(result),'physics_path':PHYSICS_PATH,
            'physics_baseline_sha256':hashlib.sha256(original_jsb).hexdigest(),
            'physics_modified_sha256':hashlib.sha256(modified_jsb).hexdigest(),
            'physics_file_size':len(modified_jsb),'repacked_block_size':len(new_block),
            'compressed_size_delta':delta,'modified_parameter_count':len(diff),
            'modified_numeric_slots':sum(len(v['before']) for v in diff.values()),
            'validated_resource_count':len(entries),'offsets_rewritten':changed_offsets,
            'gameplay_tested':False, 'new_animations_added':False, 'new_tactical_ai_added':False,
            'version':'1.1-Duels', 'source_physics_edition':ALLOWED_INPUT_PHYSICS_SHA256[source_physics_sha256],
            'group_counts':{name:len(group) for name,group in PATCH_GROUPS.items()},
            'changes':diff}
    report_output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f'PASS: {len(entries)} archive resources preserved; {len(diff)} parameters / {report["modified_numeric_slots"]} slots edited')
    print('Build:',output,'bytes:',len(result),'sha256:',report['output_sha256'])
    print('Compressed block change:',delta,'bytes; dependent offsets rewritten:',changed_offsets)
    print('GAMEPLAY TEST: NOT RUN (requires FM24 on user computer)')
    return report

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',help='Path to your existing FM24 simatch.fmf')
    ap.add_argument('--out-dir',default='.',help='Destination folder')
    args=ap.parse_args()
    src=Path(args.source);out=Path(args.out_dir);out.mkdir(exist_ok=True,parents=True)
    if not src.exists():ap.error('Source file does not exist')
    build(src,out/'EM24_Natural_Flair_v1.1_Duels.fmf',
          out/'physical_constraints_EM24_v1.1_Duels.jsb',out/'EM24_v1.1_Duels_BUILD_REPORT.json')
if __name__=='__main__':main()
