# Lightning-rod App

This is a cross-platform app for the Openstack Lightning-rod Agent. This app has been built using [BeeWare](https://beeware.org/), a suite of tools for developing Python applications across different platforms and devices, and the main goal of this application is indeed to enable the usage of Lightning-rod on a wide range of platforms and devices.


## About Openstack Lightning-rod

Stack4Things is an OpenStack-based Internet of Things framework developed by the Mobile and Distributed Systems Lab (MDSLab) at the University of Messina, Italy. Stack4Things is an open source project that helps you in managing IoT device fleets without caring about their physical location, their network configuration, their underlying technology. It is a Cloud-oriented horizontal solution providing IoT object virtualization, customization, and orchestration. Stack4Things provides you with an out-of-the-box experience on several of the most popular embedded and mobile systems.
More details can be found on the [Stack4Things website](http://stack4things.unime.it/).

## About the App
The App offers a minimal interface to start and stop the Lightning-rod Agent, alongside the possibility to see in-app the execution logs and edit the Lightning-rod configuration files as you would on a Linux host. Furthermore the original Web Control Panel was maintained so you can configure the agent from your browser, your phone's browser or just any other device on the same local network.

<div style="display: flex; gap: 1000px;">
  <img src="https://github.com/Hikari1026/LightningRodApp/assets/26839458/a18e3bd2-b3c7-44ab-bf08-6b71bacb6fc5" alt="Image 1" />
  <img src="https://github.com/Hikari1026/LightningRodApp/assets/26839458/66df3314-d793-46ab-a1de-5244df706f07" alt="Image 2" />
</div>


Currently not every features is available mostly due to Android and iOS security limitations however one key feature of the application is the possibility to reach the host machine by injecting specifically crafted plugins. You can perform shell commands on PC and Mac or even access the host SDK on iPhone and Android respectively thanks to the backends [Rubicon-objc](https://github.com/beeware/rubicon-objc) and [Chaquopy](https://chaquo.com/chaquopy/).


## Getting started
Clone the app, create a Python environment (Python 3.8 is reccomended if you plan on building the app for Android), install the dependencies and run it!

    git clone https://github.com/Hikari1026/LightningRodApp.git
    cd  LightningRodApp
    git submodule update --init --recursive
    python3.8 -m venv venv
    source  venv/bin/activate
    pip install -e stack4things-openstack-lightning-rod-app
    pip install -r requirements.txt
    python -m briefcase dev
    
After that you can refer to the official Briefcase documentation to learn how to export the application for other platforms.

Default username: **user**

Default password: **pwd** 

Remember to change them inside the app!
