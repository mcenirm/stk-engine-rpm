#
# TODO
#
# * incorporate Ansys twice-a-year release convention
#   (eg, 2023 R2 gets installed under "/usr/ansys_inc/v232")
#

Name:           stk-engine
Version:        12.7.0
Release:        2%{?dist}
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
mkdir %{buildroot}/usr
mkdir %{buildroot}/usr/ansys_inc
ln -sT usr/ansys_inc %{buildroot}/ansys_inc

tar xf %{SOURCE0} \
    --strip-components=1 \
    -C %{buildroot}/usr/ansys_inc

# these exclusions must match the ones above for ...-data.files.lst
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

mkdir -p %{buildroot}%{_bindir}
for c in connect connectconsole stkxnewuser
do
  printf '
      #!/usr/bin/bash
      export STK_INSTALL_DIR=${STK_INSTALL_DIR:-/usr/ansys_inc}
      export LD_LIBRARY_PATH=$STK_INSTALL_DIR/bin${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
      export STK_CONFIG_DIR=${STK_CONFIG_DIR:-$HOME/Documents}
      export ANSYSLMD_LICENSE_FILE=${ANSYSLMD_LICENSE_FILE:-1055@localhost}
      exec -- "$STK_INSTALL_DIR/bin/%s" "$@"
      ' $c | sed -e 's/^      //' -e '/^$/d' > %{buildroot}%{_bindir}/$c
  chmod +x %{buildroot}%{_bindir}/$c
done

# ignore rpath quirks (invalid, empty, "..")
export QA_RPATHS=0x0032


%files -f %{_builddir}/%{name}.files.lst
/ansys_inc
%{_bindir}/connect
%{_bindir}/connectconsole
%{_bindir}/stkxnewuser

%files data -f %{_builddir}/%{name}-data.files.lst


%changelog
