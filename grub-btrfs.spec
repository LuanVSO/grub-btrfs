%define dracutlibdir %{_prefix}/lib/dracut
%global commit 38cd2fa419e4c1c0f1e345a374b37c040c170047
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate 20260824

Name:           grub-btrfs
Version:        4.14^%{commitdate}git.%{shortcommit}
Release:        1%{?dist}
Summary:        grub-btrfs improves the grub bootloader by adding a btrfs snapshots sub-menu, allowing the user to boot into snapshots.

License:       GPL-3.0-only
URL:           https://github.com/Antynea/grub-btrfs
Source0:       %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Source1:       10-grub-btrfs.conf
Source2:       20-grub-btrfs.preset
Patch0:        00-fedora-fix-ups.patch

BuildArch:     noarch
BuildRequires: make
BuildRequires: systemd-rpm-macros
Requires:      btrfs-progs
Requires:      grub2
Requires:      bash
Recommends:    snapper
Recommends:    inotify-tools
Enhances:      grub2

%description
grub-btrfs improves the grub bootloader by adding a btrfs snapshots sub-menu, allowing the user to boot into snapshots.
grub-btrfs supports manual snapshots as well as snapper, timeshift, and yabsnap created snapshots.
Warning: booting read-only snapshots can be tricky
If you wish to use read-only snapshots, /var/log or even /var must be on a separate subvolume. Otherwise, make sure your snapshots are writable. See this ticket for more info.
This project includes its own solution. Refer to the documentation

%prep
%autosetup -p1 -n %{name}-%{commit}

%build

%install
%make_install SYSTEMD=true GRUB_UPDATE_EXCLUDE=true
mkdir -p %{buildroot}%{dracutlibdir}/dracut.conf.d
install -Dm0644 %{SOURCE1} %{buildroot}%{dracutlibdir}/dracut.conf.d/10-grub-btrfs.conf
install -Dm0644 %{SOURCE2} %{buildroot}%{_presetdir}/20-grub-btrfs.preset

%post
%systemd_post grub-btrfsd.service

%preun
%systemd_preun grub-btrfsd.service

%postun
%systemd_postun grub-btrfsd.service

%posttrans
if [ $1 -eq 1 ]; then
    [ -x %{_sbindir}/dracut ] && %{_sbindir}/dracut -f || :
    [ -x %{_sbindir}/grub2-mkconfig ] && \
        %{_sbindir}/grub2-mkconfig -o /etc/grub2.cfg || :
fi

%files
%license LICENSE
%doc README.md
%dir %{_sysconfdir}/default/grub-btrfs
%config %{_sysconfdir}/default/grub-btrfs/config
%{_sysconfdir}/grub.d/41_snapshots-btrfs
%{_bindir}/grub-btrfsd
%{_docdir}/grub-btrfs/initramfs-overlayfs.md
%{_mandir}/man8/grub-btrfs{,d}.8*
%{_unitdir}/grub-btrfsd.service
%{_presetdir}/20-grub-btrfs.preset

%{dracutlibdir}/dracut.conf.d/10-grub-btrfs.conf

%changelog
* Sun Aug 30 2026 Luan Vitor Simião oliveira <luanv.oliveira@outlook.com>
- initial package
