# Build RPM for STK Engine for Linux


## General preparation

1. Download STK Engine for 64-bit Linux to `rpminputs`
   * `stk_binaries_v12.7.0.tgz`
   * `stk_data_v12.7.0.tgz`


## Build RPM

1. Build RPM

   ```shell
   podman-compose -f rpmbuild-compose.yaml down -v ; podman-compose -f rpmbuild-compose.yaml up
   ```

2. Review RPMs

   ```shell
   rpm -qp builtrpms/x86_64/stk-engine-12.7.0-2.el9.x86_64.rpm -lv
   rpm -qp builtrpms/x86_64/stk-engine-data-12.7.0-2.el9.x86_64.rpm -lv
   ```


## Test RPM

1. Build test image, with RPM installed

   ```shell
   podman-compose -f rpmtest-compose.yaml build
   ```

2. Run test container

   ```shell
   podman-compose -f rpmtest-compose.yaml run -e ANSYSLMD_LICENSE_FILE=1055@LICENSEHOST rpmtest
   ```

3. Show a few details

   ```shell
   ( echo GetSTKVersion / Details ; for a in DefaultUser UserData STKHome Config Scenario AllUsers 'Database Satellite' ; do echo "GetDirectory / $a" ; done ; echo exit ) | podman-compose -f rpmtest-compose.yaml run -e ANSYSLMD_LICENSE_FILE=1055@LICENSEHOST rpmtest
   ```
