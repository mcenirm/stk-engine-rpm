#
# TODO
#
# * incorporate Ansys twice-a-year release convention
#   (eg, 2023 R2 gets installed under "/usr/ansys_inc/v232")
#

Name:           stk-engine
Version:        12.7.0
Release:        1%{?dist}
Summary:        Ansys STK Engine for Linux

License:        Proprietary
Source0:        stk_binaries_v%{version}.tgz
Source1:        stk_data_v%{version}.tgz
NoSource:       0
NoSource:       1

ExclusiveArch:  x86_64
BuildRequires:  coreutils >= 8.32
BuildRequires:  tar >= 1.34

Requires:       %{name}-data%{?_isa} = %{version}-%{release}

# confusion between internal provides and requires
Provides:       libNCSEcw.so()(64bit)
Provides:       libcollada14dom.so()(64bit)
Provides:       liblti_lidar_dsdk.so()(64bit)
Provides:       libltidsdk.so()(64bit)
Provides:       libminizip_kml.so()(64bit)

%description
Ansys Systems Tool Kit (STK) Engine for Linux


%package        data
Summary:        STK Engine for Linux data
%description    data


# avoid modifying the binary files
%global __brp_strip %{nil}
%global __brp_strip_comment_note %{nil}


%prep
sha256sum -c - <<'EOF'
493bcb5a02cf666ae847fc0303981c3b3f0f2d3b51cdabfde4123b6205f9d71c  %{SOURCE0}
EOF

sha256sum -c - <<'EOF'
7f9e7c1e8523766e99d21429fe7a2931f695497a788fbf0d6fbd5637d54c7940  %{SOURCE1}
EOF


%build
tar tf %{SOURCE0} \
| sed -e 's#^stk%{version}/#/usr/ansys_inc/#' \
> %{_builddir}/%{name}.files.lst

# most exclusions from https://github.com/AnalyticalGraphicsInc/STKCodeExamples/blob/master/StkEngineContainerization/linux/stk-engine-baseline/Dockerfile
# also excluding "STKData/Scripting" to avoid autoreq of "/usr/local/bin/perl"
tar tf %{SOURCE1} \
    '--exclude=*/Data/ExampleScenarios/*' \
    '--exclude=*/Data/HtmlInterface/*' \
    '--exclude=*/Data/HtmlUtilities/*' \
    '--exclude=*/Data/LicAndReg/*' \
    '--exclude=*/Data/Resources/*' \
    '--exclude=*/Data/Viewer/*' \
    '--exclude=*/STKData/Scripting/*' \
    '--exclude=*/STKData/VO/*' \
| sed -e 's#^stk%{version}/#/usr/ansys_inc/#' \
      -e s/^/\"/ -e s/\$/\"/ \
> %{_builddir}/%{name}-data.files.lst


%install

mkdir %{buildroot}%{_sysconfdir}
mkdir %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo /usr/ansys_inc/bin > %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}.conf

mkdir %{buildroot}%{_sysconfdir}/profile.d
echo > %{buildroot}%{_sysconfdir}/profile.d/%{name}.csh <<'EOF'
if ( ${euid} > 0 ) then
  if ( ${?STK_INSTALL_DIR} ) then
    if ( "$STK_INSTALL_DIR" != "" ) then
      goto skip_stk_install_dir
    endif
  endif
  setenv STK_INSTALL_DIR /usr/ansys_inc
  skip_stk_install_dir:

  switch (":${PATH}:")
    case "*:${STK_INSTALL_DIR}/bin:*":
      breaksw
    default:
      set path = ( ${path:q} ${STK_INSTALL_DIR:q}/bin )
      breaksw
  endsw

  if ( $?STK_CONFIG_DIR ) then
    if ( "$STK_CONFIG_DIR" != "" ) then
      goto skip_stk_config_dir
    endif
  endif
  setenv STK_CONFIG_DIR ~/Documents
  skip_stk_config_dir:
endif
EOF
echo > %{buildroot}%{_sysconfdir}/profile.d/%{name}.sh <<'EOF'
if [ "${EUID:-0}" != "0" ]; then
  [ -n "${STK_INSTALL_DIR:-}" ] || export STK_INSTALL_DIR=/usr/ansys_inc
  case ":$PATH:" in
    *:$STK_INSTALL_DIR/bin:*) ;;
    *) PATH=$PATH:$STK_INSTALL_DIR/bin ;;
  esac
  [ -n "${STK_CONFIG_DIR:-}" ] || export STK_CONFIG_DIR=$HOME/Documents
fi
EOF

mkdir %{buildroot}/usr
mkdir %{buildroot}/usr/ansys_inc
ln -sT usr/ansys_inc %{buildroot}/ansys_inc

tar xf %{SOURCE0} \
    --strip-components=1 \
    -C %{buildroot}/usr/ansys_inc
tar xf %{SOURCE1} \
    '--exclude=*/Data/ExampleScenarios/*' \
    '--exclude=*/Data/HtmlInterface/*' \
    '--exclude=*/Data/HtmlUtilities/*' \
    '--exclude=*/Data/LicAndReg/*' \
    '--exclude=*/Data/Resources/*' \
    '--exclude=*/Data/Viewer/*' \
    '--exclude=*/STKData/Scripting/*' \
    '--exclude=*/STKData/VO/*' \
    --strip-components=1 \
    -C %{buildroot}/usr/ansys_inc

# ignore rpath quirks (invalid, empty, "..")
export QA_RPATHS=0x0032


%files -f %{_builddir}/%{name}.files.lst
/ansys_inc
%{_sysconfdir}/ld.so.conf.d/%{name}.conf
%{_sysconfdir}/profile.d/%{name}.csh
%{_sysconfdir}/profile.d/%{name}.sh

%files data -f %{_builddir}/%{name}-data.files.lst


%changelog
