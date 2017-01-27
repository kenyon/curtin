from curtin.util import get_platform_arch


class _ReleaseBase(object):
    repo = "maas-daily"
    arch = get_platform_arch()


class _UbuntuBase(_ReleaseBase):
    distro = "ubuntu"


class _CentosFromUbuntuBase(_UbuntuBase):
    # base for installing centos tarballs from ubuntu base
    target_distro = "centos"


class _Centos70FromXenialBase(_CentosFromUbuntuBase):
    # release for boot
    release = "xenial"
    # release for target
    target_release = "centos70"


class _Centos66FromXenialBase(_CentosFromUbuntuBase):
    release = "xenial"
    target_release = "centos66"


class _PreciseBase(_UbuntuBase):
    release = "precise"


class _PreciseHWET(_UbuntuBase):
    release = "precise"
    krel = "trusty"


class _TrustyBase(_UbuntuBase):
    release = "trusty"


class _TrustyHWEU(_UbuntuBase):
    release = "trusty"
    krel = "utopic"


class _TrustyHWEV(_UbuntuBase):
    release = "trusty"
    krel = "vivid"


class _TrustyHWEW(_UbuntuBase):
    release = "trusty"
    krel = "wily"


class _TrustyHWEX(_UbuntuBase):
    release = "trusty"
    krel = "xenial"


class _TrustyFromXenial(_UbuntuBase):
    release = "xenial"
    target_release = "trusty"


class _VividBase(_UbuntuBase):
    release = "vivid"


class _WilyBase(_UbuntuBase):
    release = "wily"


class _XenialBase(_UbuntuBase):
    release = "xenial"


class _XenialHWEY(_UbuntuBase):
    release = "xenial"
    krel = "yakkety"


class _XenialHWEZ(_UbuntuBase):
    release = "xenial"
    krel = "zesty"


class _YakketyBase(_UbuntuBase):
    release = "yakkety"


class _ZestyBase(_UbuntuBase):
    release = "zesty"


class _Releases(object):
    precise = _PreciseBase
    precise_hwe_t = _PreciseHWET
    trusty = _TrustyBase
    trusty_hwe_u = _TrustyHWEU
    trusty_hwe_v = _TrustyHWEV
    trusty_hwe_w = _TrustyHWEW
    trusty_hwe_x = _TrustyHWEX
    trustyfromxenial = _TrustyFromXenial
    vivid = _VividBase
    wily = _WilyBase
    xenial = _XenialBase
    xenial_hwe_y = _XenialHWEY
    xenial_hwe_z = _XenialHWEZ
    yakkety = _YakketyBase
    zesty = _ZestyBase


class _CentosReleases(object):
    centos70fromxenial = _Centos70FromXenialBase
    centos66fromxenial = _Centos66FromXenialBase


base_vm_classes = _Releases
centos_base_vm_classes = _CentosReleases

# vi: ts=4 expandtab syntax=python
