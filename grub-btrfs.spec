%global dracutlibdir %{_prefix}/lib/dracut

# git snapshot because last tagged release couldn't detect snapper snapshots during testing
%global commit 38cd2fa419e4c1c0f1e345a374b37c040c170047
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate 20260824

Name:           grub-btrfs
Version:        4.14^%{commitdate}.git%{shortcommit}
Release:        %autorelease
Summary:        Adds a btrfs snapshots sub-menu to grub
# https://github.com/Antynea/grub-btrfs/issues/313
License:        GPL-3.0-only
URL:            https://github.com/Antynea/grub-btrfs
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Source1:        10-grub-btrfs.conf
# not possible to enable grub-btrfsd.service via preset yet because snapper requires manual intervention to enable root snapshots

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
BuildRequires:  ShellCheck

Requires:       btrfs-progs
Requires:       grub2-common
Requires:       dracut
Requires(post): dracut
Requires(post): grub2-tools

Recommends:     (snapper or timeshift)
Recommends:     inotify-tools
Enhances:       grub2-common

%description
grub-btrfs improves the grub bootloader by adding a btrfs snapshots sub-menu,
allowing the user to boot into snapshots.
grub-btrfs supports manual snapshots as well as snapper, timeshift, and yabsnap
created snapshots.

%prep
%autosetup -C -p1
# uneeded shebang line in config file, remove it to avoid warnings
sed -i '1d' config

%build

%install
%make_install SYSTEMD=true GRUB_UPDATE_EXCLUDE=true
mkdir -p %{buildroot}%{dracutlibdir}/dracut.conf.d
install -pDm0644 %{SOURCE1} %{buildroot}%{dracutlibdir}/dracut.conf.d/10-grub-btrfs.conf

%post
%systemd_post grub-btrfsd.service
if [ -x %{_sbindir}/dracut ] && [ -e /boot/vmlinuz-$(uname -r) ]; then
    %{_sbindir}/dracut -f --kver "$(uname -r)" || :
fi

if [ -x /usr/sbin/grub2-mkconfig ]; then
    if [ -L /etc/grub2.cfg ] || [ -f /etc/grub2.cfg ]; then
        /usr/sbin/grub2-mkconfig -o "$(readlink -f /etc/grub2.cfg)" || :
    fi
fi

%preun
%systemd_preun grub-btrfsd.service

%postun
%systemd_postun grub-btrfsd.service

%check
shellcheck -S error -s bash %{buildroot}%{_sysconfdir}/grub.d/41_snapshots-btrfs %{buildroot}%{_sysconfdir}/default/grub-btrfs/config

%files
%license LICENSE
%doc README.md
%{_pkgdocdir}/initramfs-overlayfs.md
%{_mandir}/man8/grub-btrfs{,d}.8*
%dir %{_sysconfdir}/default/grub-btrfs
%config(noreplace) %{_sysconfdir}/default/grub-btrfs/config

# this script is the main entry point for grub-btrfs, and is called by grub2-mkconfig
# upgrading without overwriting this file is not recommended, as it may break grub-btrfs functionality
%{_sysconfdir}/grub.d/41_snapshots-btrfs

%{_unitdir}/grub-btrfsd.service
%attr(0755,root,root) %{_bindir}/grub-btrfsd
%attr(0644,root,root) %ghost %config(noreplace) /boot/grub2/grub-btrfs.cfg
#{_presetdir}/20-grub-btrfs.preset
%{dracutlibdir}/dracut.conf.d/10-grub-btrfs.conf

%changelog
%autochangelog
