# 02 - GNU Radio and USRP

## Open GNU Radio Companion

```bash
sudo gnuradio-companion
```

## List USRP Devices

```bash
sudo uhd_find_devices
```

Expected result:

- UHD lists the connected USRP device.
- The output shows device information such as type, serial number, and address.

## Notes

- Run the TAP setup before starting the flowgraph.
- Check USRP detection before running the flowgraph.
- If the `.grc` file uses a TAP block, confirm it is configured to use `tap0`.
