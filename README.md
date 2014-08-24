PyMine
======

<img style="text-align:center;" src="https://cloud.githubusercontent.com/assets/8518514/4023774/0eca78ec-2ba6-11e4-8844-81199da62058.jpeg"/>

The Minecraft server for Linux is not particularly suited for being...well...a server. The Java process runs in the foreground, taking up your entire session. This leads many people to resort to tactics, such as Screen, for shoving the process into the background. The result is something that is not really well suited for on-the-fly control of the Minecraft server and does not work well with modern init systems.

PyMine is a traditional Unix daemon that manages a Minecraft subprocess. Beyond the small set of control keywords (start|stop|restart|status|backup) communication with the Minecraft server via PyMine is completely transparent. This allows for awesomeness such as:

$ pymine start
$ pymine weather rain
$ pymine weather clear
$ pymine time set 6000
$ pymine kill BillBobb
$ pymine say STOP HITTING YOURSELF!
$ pymine stop

If PyMine is executed with no arguments then an interactive session is started.

Dependencies:
python-daemon
pyyaml
psutils
