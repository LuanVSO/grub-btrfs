%define dracutlibdir %{_prefix}/lib/dracut

# git snapshot because last tagged release couldn't detect snapper snapshots during testing
%global commit 38cd2fa419e4c1c0f1e345a374b37c040c170047
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate 20260824

Name:           grub-btrfs
Version:        4.14^%{commitdate}git.%{shortcommit}
Release:        %autorelease
Summary:        Adds a btrfs snapshots sub-menu to grub
License:        GPL-3.0-only
URL:            https://github.com/Antynea/grub-btrfs
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Source1:        10-grub-btrfs.conf
# not possible to enable grub-btrfsd.service via preset yet because snapper requires manual intervention to enable / snapshots
#Source2:        20-grub-btrfs.preset

# fedora specific paths, commands and options
Patch0:         00-fedora-config-options.patch
# allow non-root install if destdir is set.
# https://github.com/Antynea/grub-btrfs/pull/445
Patch1:         01-ignore-root-check-with-destdir.patch

BuildArch:      noarch
BuildRequires:  make
BuildRequires:  systemd-rpm-macros
BuildRequires:  coreutils
BuildRequires:  sed
Requires:       btrfs-progs
Requires:       grub2
Requires:       dracut
Requires:       bash
Recommends:     (snapper or timeshift)
Recommends:     inotify-tools
Enhances:       grub2

%description
grub-btrfs improves the grub bootloader by adding a btrfs snapshots sub-menu,
allowing the user to boot into snapshots.
grub-btrfs supports manual snapshots as well as snapper, timeshift, and yabsnap
created snapshots.

%prep
%autosetup -p1 -n %{name}-%{commit}
# uneeded shebang line in config file, remove it to avoid warnings
sed -i '1d' config

%build

%install
%make_install SYSTEMD=true GRUB_UPDATE_EXCLUDE=true
mkdir -p %{buildroot}%{dracutlibdir}/dracut.conf.d
install -pDm0644 %{SOURCE1} %{buildroot}%{dracutlibdir}/dracut.conf.d/10-grub-btrfs.conf
#install -pDm0644 {SOURCE2} {buildroot}{_presetdir}/20-grub-btrfs.preset

%post
%systemd_post grub-btrfsd.service

%preun
%systemd_preun grub-btrfsd.service

%postun
%systemd_postun grub-btrfsd.service
 if [ $1 -eq 0 ]; then
    %{_sbindir}/grub2-mkconfig -o /etc/grub2.cfg 2>/dev/null || :
 fi

%posttrans
if [ $1 -eq 1 ]; then
    %{_sbindir}/grub2-mkconfig -o /etc/grub2.cfg 2>/dev/null || :
    %{_sbindir}/dracut -f || :
fi

%check

%files
%license LICENSE
%doc README.md
%{_pkgdocdir}/initramfs-overlayfs.md
%{_mandir}/man8/grub-btrfs{,d}.8*
%attr(0700,root,root) %dir %{_sysconfdir}/default/grub-btrfs
%config(noreplace) %{_sysconfdir}/default/grub-btrfs/config

# this script is the main entry point for grub-btrfs, and is called by grub2-mkconfig
# upgrading without overwriting this file is not recommended, as it may break grub-btrfs functionality
%attr(0755,root,root) %config %{_sysconfdir}/grub.d/41_snapshots-btrfs

%attr(0755,root,root) %{_bindir}/grub-btrfsd
%attr(0644,root,root) %{_unitdir}/grub-btrfsd.service
%attr(0644,root,root) %ghost %config(noreplace) /boot/grub2/grub-btrfs.cfg
#{_presetdir}/20-grub-btrfs.preset
%{dracutlibdir}/dracut.conf.d/10-grub-btrfs.conf

%changelog
%autochangelog
