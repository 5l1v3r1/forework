import struct
from collections import namedtuple

from ..basetask import BaseTask, find_tasks_by_filetype
from .. import utils

# TODO handle extended partitions
# TODO handle cases where the sector size is not 512 but 4096
# TODO use libmagic

SECTOR_SIZE = 512

logger = utils.get_logger(__name__)

MBR_FMT = (
    '<'  # little-endian
    '446x'  # code
    '16s'  # first partition
    '16s'  # second partition
    '16s'  # third partition
    '16s'  # fourth partition
    '2s'  # signature
)

MBRType = namedtuple(
    'MBR',
    [
        'partition_1',
        'partition_2',
        'partition_3',
        'partition_4',
        'signature',
    ],
)

MBR_PARTITION_FMT = (
    '<'  # little-endian
    'B'  # status
    '3s'  # chs_first
    'B'  # type
    '3s'  # chs_last
    'L'  # LBA
    'L'  # sectors
)

MBRPartitionType = namedtuple(
    'MBRPartition',
    [
        'status',
        'chs_first',
        'type',
        'chs_last',
        'lba',
        'sectors',
    ],
)


def parse_chs(chs):
    # http://thestarman.pcministry.com/asm/mbr/PartTables.htm
    c = chs[2] + ((chs[1] & 0xc0) << 8)
    s = chs[1] & 0x3f
    h = chs[0]
    return c, h, s


def chs_to_lba(c, h, s, hpc=16, spt=63):
    # https://en.wikipedia.org/wiki/Logical_block_addressing#CHS_conversion
    # HPC stands for Heads Per Cylinder, default=16
    # SPT stands for Sectors Per Track, default=63
    return (c * hpc + h) * spt + (s - 1)


def lba_to_chs(lba, hpc=16, spt=63):
    # https://en.wikipedia.org/wiki/Logical_block_addressing#CHS_conversion
    # HPC stands for Heads Per Cylinder, default=16
    # SPT stands for Sectors Per Track, default=63
    c = lba / (hpc * spt)
    h = (lba / spt) % hpc
    s = lba % spt + 1
    return c, h, s


class MBR(BaseTask):
    '''
    Task to handle MBR objects
    '''

    MAGIC_PATTERN = '^DOS/MBR boot sector;.+'

    def __init__(self, path, use_libmagic=False, *args, **kwargs):
        self._use_libmagic = use_libmagic
        BaseTask.__init__(self, path, *args, **kwargs)

    def run(self):
        with open(self._path, 'rb') as fd:
            fd.seek(self._offset)
            data = fd.read(struct.calcsize(MBR_FMT))
        mbr = MBRType(*struct.unpack(MBR_FMT, data))
        if mbr.signature != bytes(b'\x55\xaa'):
            self.add_warning(
                'Bad MBR signature. Got: {got!r}, expected: {exp!r}'.format(
                    got=mbr.signature,
                    exp=0xaa55,
                ))
        part_types = []
        for part_num in (1, 2, 3, 4):
            # FIXME handle extended partitions, type 0x5
            part_data = getattr(mbr, 'partition_{n}'.format(n=part_num))
            partition = MBRPartitionType(
                *struct.unpack(MBR_PARTITION_FMT, part_data))
            if partition.status not in (0x00, 0x80):
                self.add_warning(
                    'partition {n}: status is neither 0x00 nor 0x80: got {v}'
                    .format(
                        n=part_num,
                        v=partition.status,
                    )
                )
            c, h, s = parse_chs(partition.chs_first)
            if s == 0:
                self.add_warning('partition {n}: sector in CHS should not be 0'
                                 .format(n=part_num))
            if c == 0xff:
                self.add_warning(
                    'partition {n}: cylinder in CHS should not be 0xff'.format(
                        n=part_num,
                    )
                )
            part_type = partition_types[partition.type][0]
            part_types.append(part_type)
            if partition.chs_first == '\xff\xff\xfe':
                use_lba = True

            # if CHS == LBA, then we should use LBA, unless one of the
            # exceptions below apply
            chs_equivalent = chs_to_lba(c, h, s)
            use_lba = chs_equivalent == partition.lba

            # exceptions by partition type
            if part_type in (0x06, 0x0b):  # CHS-mapped fat-16/32
                use_lba = False
                if partition.chs_first == '\xff\xff\xfe':
                    self.add_warning(
                        'partition {n}: CHS value set to 0xfe 0xff 0xff but '
                        'the partition type requires CHS'.format(n=part_num))
            elif part_type in (0x0e, 0x0c):  # LBA-mapped fat-16/32
                use_lba = True

            offset = partition.lba if use_lba else chs_equivalent
            # tell the scheduler what to do with each partition found
            next_task = find_tasks_by_filetype(part_type)
            if next_task:
                self.add_next_task({
                    'name': next_task,
                    'path': self._path,
                    'offset': offset,
                })
        self._result = part_types
        self.done = True


# from
# https://github.com/insomniacslk/partlist/blob/master/output/partitions.json
partition_types = {
    0: [
        "Empty"
    ],
    1: [
        "DOS 12-bit FAT"
    ],
    2: [
        "XENIX root"
    ],
    3: [
        "XENIX /usr"
    ],
    4: [
        "DOS 3.0+ 16-bit FAT (up to 32M)"
    ],
    5: [
        "DOS 3.3+ Extended Partition"
    ],
    6: [
        "DOS 3.31+ 16-bit FAT (over 32M)"
    ],
    7: [
        "OS/2 IFS (e.g., HPFS)",
        "Windows NT NTFS",
        "exFAT",
        "Advanced Unix",
        "QNX2.x pre-1988 (see below under IDs 4d-4f)"
    ],
    8: [
        "OS/2 (v1.0-1.3 only)",
        "AIX boot partition",
        "SplitDrive",
        "Commodore DOS",
        "DELL partition spanning multiple drives",
        "QNX 1.x and 2.x (\"qny\")"
    ],
    9: [
        "AIX data partition",
        "Coherent filesystem",
        "QNX 1.x and 2.x (\"qnz\")"
    ],
    10: [
        "OS/2 Boot Manager",
        "Coherent swap partition",
        "OPUS"
    ],
    11: [
        "WIN95 OSR2 FAT32"
    ],
    12: [
        "WIN95 OSR2 FAT32, LBA-mapped"
    ],
    13: [
        "SILICON SAFE"
    ],
    14: [
        "WIN95: DOS 16-bit FAT, LBA-mapped"
    ],
    15: [
        "WIN95: Extended partition, LBA-mapped"
    ],
    16: [
        "OPUS (?)"
    ],
    17: [
        "Hidden DOS 12-bit FAT"
    ],
    18: [
        "Configuration/diagnostics partition"
    ],
    20: [
        "Hidden DOS 16-bit FAT &lt;32M"
    ],
    22: [
        "Hidden DOS 16-bit FAT &gt;=32M"
    ],
    23: [
        "Hidden IFS (e.g., HPFS)"
    ],
    24: [
        "AST SmartSleep Partition"
    ],
    25: [
        "Unused"
    ],
    27: [
        "Hidden WIN95 OSR2 FAT32"
    ],
    28: [
        "Hidden WIN95 OSR2 FAT32, LBA-mapped"
    ],
    30: [
        "Hidden WIN95 16-bit FAT, LBA-mapped"
    ],
    32: [
        "Unused"
    ],
    33: [
        "Reserved",
        "Unused"
    ],
    34: [
        "Unused"
    ],
    35: [
        "Reserved"
    ],
    36: [
        "NEC DOS 3.x"
    ],
    38: [
        "Reserved"
    ],
    39: [
        "PQservice",
        "Windows RE hidden partition",
        "MirOS partition",
        "RouterBOOT kernel partition"
    ],
    42: [
        "AtheOS File System (AFS)"
    ],
    49: [
        "Reserved"
    ],
    50: [
        "NOS"
    ],
    51: [
        "Reserved"
    ],
    52: [
        "Reserved"
    ],
    53: [
        "JFS on OS/2 or eCS "
    ],
    54: [
        "Reserved"
    ],
    56: [
        "THEOS ver 3.2 2gb partition"
    ],
    57: [
        "Plan 9 partition",
        "THEOS ver 4 spanned partition"
    ],
    58: [
        "THEOS ver 4 4gb partition"
    ],
    59: [
        "THEOS ver 4 extended partition"
    ],
    60: [
        "PartitionMagic recovery partition"
    ],
    61: [
        "Hidden NetWare"
    ],
    64: [
        "Venix 80286",
        "PICK"
    ],
    65: [
        "Linux/MINIX (sharing disk with DRDOS)",
        "Personal RISC Boot",
        "PPC PReP (Power PC Reference Platform) Boot"
    ],
    66: [
        "Linux swap (sharing disk with DRDOS)",
        "SFS (Secure Filesystem)",
        "Windows 2000 dynamic extended partition marker"
    ],
    67: [
        "Linux native (sharing disk with DRDOS)"
    ],
    68: [
        "GoBack partition"
    ],
    69: [
        "Boot-US boot manager",
        "Priam",
        "EUMEL/Elan "
    ],
    70: [
        "EUMEL/Elan "
    ],
    71: [
        "EUMEL/Elan "
    ],
    72: [
        "EUMEL/Elan "
    ],
    74: [
        "Mark Aitchison's ALFS/THIN lightweight filesystem for DOS",
        "AdaOS Aquila (Withdrawn)"
    ],
    76: [
        "Oberon partition"
    ],
    77: [
        "QNX4.x"
    ],
    78: [
        "QNX4.x 2nd part"
    ],
    79: [
        "QNX4.x 3rd part",
        "Oberon partition"
    ],
    80: [
        "OnTrack Disk Manager (older versions) RO",
        "Lynx RTOS",
        "Native Oberon (alt)"
    ],
    81: [
        "OnTrack Disk Manager RW (DM6 Aux1)",
        "Novell"
    ],
    82: [
        "CP/M",
        "Microport SysV/AT"
    ],
    83: [
        "Disk Manager 6.0 Aux3"
    ],
    84: [
        "Disk Manager 6.0 Dynamic Drive Overlay (DDO)"
    ],
    85: [
        "EZ-Drive"
    ],
    86: [
        "Golden Bow VFeature Partitioned Volume.",
        "DM converted to EZ-BIOS"
    ],
    87: [
        "DrivePro",
        "VNDI Partition"
    ],
    92: [
        "Priam EDisk"
    ],
    97: [
        "SpeedStor"
    ],
    99: [
        "Unix System V (SCO, ISC Unix, UnixWare, ...), Mach, GNU Hurd"
    ],
    100: [
        "PC-ARMOUR protected partition",
        "Novell Netware 286, 2.xx"
    ],
    101: [
        "Novell Netware 386, 3.xx or 4.xx"
    ],
    102: [
        "Novell Netware SMS Partition"
    ],
    103: [
        "Novell"
    ],
    104: [
        "Novell"
    ],
    105: [
        "Novell Netware 5+, Novell Netware NSS Partition"
    ],
    110: [
        "??"
    ],
    112: [
        "DiskSecure Multi-Boot"
    ],
    113: [
        "Reserved"
    ],
    114: [
        "V7/x86"
    ],
    115: [
        "Reserved"
    ],
    116: [
        "Reserved",
        "Scramdisk partition"
    ],
    117: [
        "IBM PC/IX"
    ],
    118: [
        "Reserved"
    ],
    119: [
        "M2FS/M2CS partition",
        "VNDI Partition"
    ],
    120: [
        "XOSL FS"
    ],
    126: [
        "Unused"
    ],
    127: [
        "Unused"
    ],
    128: [
        "MINIX until 1.4a"
    ],
    129: [
        "MINIX since 1.4b, early Linux",
        "Mitac disk manager"
    ],
    130: [
        "Prime",
        "Solaris x86",
        "Linux swap"
    ],
    131: [
        "Linux native partition"
    ],
    132: [
        "OS/2 hidden C: drive",
        "Hibernation partition"
    ],
    133: [
        "Linux extended partition"
    ],
    134: [
        "Old Linux RAID partition superblock",
        "FAT16 volume set"
    ],
    135: [
        "NTFS volume set"
    ],
    136: [
        "Linux plaintext partition table"
    ],
    138: [
        "Linux Kernel Partition (used by AiR-BOOT)"
    ],
    139: [
        "Legacy Fault Tolerant FAT32 volume"
    ],
    140: [
        "Legacy Fault Tolerant FAT32 volume using BIOS extd INT 13h"
    ],
    141: [
        "Free FDISK 0.96+ hidden Primary DOS FAT12 partitition"
    ],
    142: [
        "Linux Logical Volume Manager partition"
    ],
    144: [
        "Free FDISK 0.96+ hidden Primary DOS FAT16 partitition"
    ],
    145: [
        "Free FDISK 0.96+ hidden DOS extended partitition"
    ],
    146: [
        "Free FDISK 0.96+ hidden Primary DOS large FAT16 partitition"
    ],
    147: [
        "Hidden Linux native partition",
        "Amoeba"
    ],
    148: [
        "Amoeba bad block table"
    ],
    149: [
        "MIT EXOPC native partitions"
    ],
    150: [
        "CHRP ISO-9660 filesystem"
    ],
    151: [
        "Free FDISK 0.96+ hidden Primary DOS FAT32 partitition"
    ],
    152: [
        "Free FDISK 0.96+ hidden Primary DOS FAT32 partitition (LBA)",
        "Datalight ROM-DOS Super-Boot Partition"
    ],
    153: [
        "DCE376 logical drive"
    ],
    154: [
        "Free FDISK 0.96+ hidden Primary DOS FAT16 partitition (LBA)"
    ],
    155: [
        "Free FDISK 0.96+ hidden DOS extended partitition (LBA)"
    ],
    158: [
        "ForthOS partition"
    ],
    159: [
        "BSD/OS"
    ],
    160: [
        "Laptop hibernation partition"
    ],
    161: [
        "Laptop hibernation partition",
        "HP Volume Expansion (SpeedStor variant)"
    ],
    163: [
        "HP Volume Expansion (SpeedStor variant)"
    ],
    164: [
        "HP Volume Expansion (SpeedStor variant)"
    ],
    165: [
        "BSD/386, 386BSD, NetBSD, FreeBSD"
    ],
    166: [
        "OpenBSD",
        "HP Volume Expansion (SpeedStor variant)"
    ],
    167: [
        "NeXTStep"
    ],
    168: [
        "Mac OS-X"
    ],
    169: [
        "NetBSD"
    ],
    170: [
        "Olivetti Fat 12 1.44MB Service Partition"
    ],
    171: [
        "Mac OS-X Boot partition",
        "GO! partition"
    ],
    173: [
        "RISC OS ADFS"
    ],
    174: [
        "ShagOS filesystem"
    ],
    175: [
        "ShagOS swap partition",
        "MacOS X HFS"
    ],
    176: [
        "BootStar Dummy"
    ],
    177: [
        "HP Volume Expansion (SpeedStor variant)",
        "QNX Neutrino Power-Safe filesystem"
    ],
    178: [
        "QNX Neutrino Power-Safe filesystem"
    ],
    179: [
        "HP Volume Expansion (SpeedStor variant)",
        "QNX Neutrino Power-Safe filesystem"
    ],
    180: [
        "HP Volume Expansion (SpeedStor variant)"
    ],
    182: [
        "HP Volume Expansion (SpeedStor variant)",
        "Corrupted Windows NT mirror set (master), FAT16 file system"
    ],
    183: [
        "Corrupted Windows NT mirror set (master), NTFS file system",
        "BSDI BSD/386 filesystem"
    ],
    184: [
        "BSDI BSD/386 swap partition"
    ],
    187: [
        "Boot Wizard hidden"
    ],
    188: [
        "Acronis backup partition"
    ],
    189: [
        "BonnyDOS/286"
    ],
    190: [
        "Solaris 8 boot partition"
    ],
    191: [
        "New Solaris x86 partition"
    ],
    192: [
        "CTOS",
        "REAL/32 secure small partition",
        "NTFT Partition",
        "DR-DOS/Novell DOS secured partition"
    ],
    193: [
        "DRDOS/secured (FAT-12)"
    ],
    194: [
        "Unused",
        "Hidden Linux"
    ],
    195: [
        "Hidden Linux swap"
    ],
    196: [
        "DRDOS/secured (FAT-16, &lt; 32M)"
    ],
    197: [
        "DRDOS/secured (extended)"
    ],
    198: [
        "DRDOS/secured (FAT-16, &gt;= 32M)",
        "Windows NT corrupted FAT16 volume/stripe set"
    ],
    199: [
        "Windows NT corrupted NTFS volume/stripe set",
        "Syrinx boot"
    ],
    200: [
        "Reserved for DR-DOS 8.0+"
    ],
    201: [
        "Reserved for DR-DOS 8.0+"
    ],
    202: [
        "Reserved for DR-DOS 8.0+"
    ],
    203: [
        "DR-DOS 7.04+ secured FAT32 (CHS)/"
    ],
    204: [
        "DR-DOS 7.04+ secured FAT32 (LBA)/"
    ],
    205: [
        "CTOS Memdump? "
    ],
    206: [
        "DR-DOS 7.04+ FAT16X (LBA)/"
    ],
    207: [
        "DR-DOS 7.04+ secured EXT DOS (LBA)/"
    ],
    208: [
        "REAL/32 secure big partition",
        "Multiuser DOS secured partition"
    ],
    209: [
        "Old Multiuser DOS secured FAT12"
    ],
    212: [
        "Old Multiuser DOS secured FAT16 &lt;32M"
    ],
    213: [
        "Old Multiuser DOS secured extended partition"
    ],
    214: [
        "Old Multiuser DOS secured FAT16 &gt;=32M"
    ],
    216: [
        "CP/M-86"
    ],
    218: [
        "Non-FS Data",
        "Powercopy Backup"
    ],
    219: [
        "Digital Research CP/M, Concurrent CP/M, Concurrent DOS",
        "CTOS (Convergent Technologies OS -Unisys)",
        "KDG Telemetry SCPU boot"
    ],
    221: [
        "Hidden CTOS Memdump? "
    ],
    222: [
        "Dell PowerEdge Server utilities (FAT fs)"
    ],
    223: [
        "DG/UX virtual disk manager partition",
        "BootIt EMBRM"
    ],
    225: [
        "DOS access or SpeedStor 12-bit FAT extended partition"
    ],
    227: [
        "DOS R/O or SpeedStor"
    ],
    228: [
        "SpeedStor 16-bit FAT extended partition &lt; 1024 cyl."
    ],
    230: [
        "Storage Dimensions SpeedStor"
    ],
    232: [
        "LUKS"
    ],
    234: [
        "Rufus extra partition",
        "Freedesktop boot"
    ],
    235: [
        "BeOS BFS"
    ],
    236: [
        "SkyOS SkyFS"
    ],
    237: [
        "Unused"
    ],
    238: [
        "Indication that this legacy MBR is followed by an EFI header"
    ],
    239: [
        "Partition that contains an EFI file system"
    ],
    240: [
        "Linux/PA-RISC boot loader"
    ],
    241: [
        "Storage Dimensions SpeedStor"
    ],
    242: [
        "DOS 3.3+ secondary partition"
    ],
    243: [
        "Reserved"
    ],
    244: [
        "SpeedStor large partition",
        "Prologue single-volume partition"
    ],
    245: [
        "Prologue multi-volume partition"
    ],
    246: [
        "Storage Dimensions SpeedStor"
    ],
    247: [
        "DDRdrive Solid State File System"
    ],
    249: [
        "pCache"
    ],
    250: [
        "Bochs"
    ],
    251: [
        "VMware File System partition"
    ],
    252: [
        "VMware Swap partition"
    ],
    253: [
        "Linux raid partition with autodetect using persistent superblock"
    ],
    254: [
        "SpeedStor &gt; 1024 cyl.",
        "LANstep",
        "Windows NT Disk Administrator hidden partition",
        "Linux Logical Volume Manager partition (old)"
    ],
    255: [
        "Xenix Bad Block Table"
    ]
}
