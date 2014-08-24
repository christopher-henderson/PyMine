PyMine
======

<div align="center"><a href="https://github.com/christopher-henderson/PyMine"><img src="https://cloud.githubusercontent.com/assets/8518514/4023774/0eca78ec-2ba6-11e4-8844-81199da62058.jpeg"/></a></div>
<div align="center"><strong>"That sure is a nice daemon you have there..."</strong></div>
<p></p>
The Minecraft server for Linux is not particularly suited for being...well...a server. The Java process runs in the foreground, taking up your entire session. This leads many people to resort to tactics, such as Screen, for shoving the process into the background. The result is something that is not really well suited for on-the-fly control of the Minecraft server and does not work well with modern init systems.

PyMine is a traditional Unix daemon that manages a Minecraft subprocess. Beyond the small set of control keywords (start|stop|restart|status|backup) communication with the Minecraft server via PyMine is completely transparent. This allows for awesomeness such as:

$ pymine start<br>
$ pymine weather rain<br>
$ pymine weather clear<br>
$ pymine time set 6000<br>
$ pymine kill BillBobb<br>
$ pymine say STOP HITTING YOURSELF!<br>
$ pymine stop

If PyMine is executed with no arguments then an interactive session is started.

Creation of world backups are supported through the "backup" command.

A systemd service file has been included for hook-ups into the init system.

$ sudo ln -s pymine /usr/bin/pymine<br>
$ sudo mv pymine.service /usr/lib/systemd/system<br>
$ sudo systemctl enable pymine<br>
$ sudo systemctl start pymine<br>

<p><strong>Dependencies:</strong><br>
python-daemon<br>
pyyaml<br>
psutils<br></p>
