# OSDR
### Overview

The OSDR Q10 is one of Orion Innovations' derivative software defined radio products, capable of transmitting and receiving any wideband RF signal via four 8-bit fully synchronized channels. 


### Introduction

The OSDR line of software radios works by converting digital samples into an analog waveform at the physical layer and vice versa, thereby allowing the user to programmatically define her/his modulation scheme. In particular, the OSDR Q10 features an onboard Kintex-7 325T FPGA which is automatically configured on power-up by an SAM9263 processor running a barebones Linux OS. By default, this FPGA configuration simply transmits and receives samples through the USB3 port; however, the bitstream can easily be changed by using SSH or FTP to copy and/or replace the old bitstream with the desired one. 

The OSDR Q10 has three different peripheries for data transfer and/or streaming. By default, the USB3 port is used to stream data.

- USB3.1 for streaming I/O
- USB2.0 (x2) for external media
- 100Mbps Ethernet for debugging and updates


### Applications

The OSDR Q10 is intended primarily for advanced users and/or research groups, while the OSDR S10（coming soon） is more suitable for simple applications.


### Parameters

The table below lists various parameters for the OSDR Q10.

| Parameter                   | Value           | Notes                   |
|:--------------------------- |:---------------:|:------------------------|
| Number of channels          | 4               | Baseband synchronized   |
| FPGA logic cells            | 326,080         | Xilinx Kintex-7 325T    |
| Onboard reference frequency | 40MHz           |                         |
| Onboard reference accuracy  | +-10ppm         |                         |
| Data transfer speed         | 3.3Gsps         | USB3.1, theoretical max |
| Maximum sample rate         | 61.44Msps       |                         |
| Maximum RF bandwidth        | 56MHz           |                         |
| Carrier frequency range     | 100MHz - 6GHz   |                         |
| Carrier hopping time        | 41.25Msps       | Dependent on "hop size" |
| Maximum gain @800MHz        | 74.5dB          | As per RF IC datasheet  |
| Maximum gain @2.3GHz        | 73.0db          | As per RF IC datasheet  |
| Maximum gain @5.5GHz        | 65.5dB          | As per RF IC datasheet  |
| Maximum gain @6.0GHz        | ~60dB           | Empirically measured    |


### Drivers and Documentation

For instructions on how to get started, please visit [the official OSDR github repository](https://github.com/OrionInnov/OSDR).

As a new product, our documentation is not 100% complete. Furthermore, the driver package currently only works in Linux, i.e. there is no Windows or Mac driver support just yet. If you have any questions and potential feature requests, feel free to open an issue on Github, or you can contact us directly at contact@oriontech.io. Thank you for bearing with us as we work to improve it!
