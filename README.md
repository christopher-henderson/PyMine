PyMine
======

<div align="center"><a href="https://github.com/christopher-henderson/PyMine"><img src="https://cloud.githubusercontent.com/assets/8518514/4023774/0eca78ec-2ba6-11e4-8844-81199da62058.jpeg"/></a></div>
<div align="center"><h3>"That sure is a nice server you have there..."</h3></div>
<p></p>
The Minecraft server for Linux is not particularly suited for being...well...a server. The Java process runs in the foreground, taking up your entire session. This leads many people to resort to tactics, such as Screen, for shoving the process into the background. The result is something that is not really well suited for on-the-fly control of the Minecraft server and does not work well with modern init systems.

PyMine is a way to manage one-to-many Minecraft servers from a single point of control. Commands given to PyMine are transparently demultiplexed to your Minecraft servers based on your criteria.

The PyMine config is a YAML file whose structure is inspired by Nginx. If you are familiar with Nginx's "block" style of configuration, then you should feel at home here. The idea is that the top, global, level of the config file is for PyMine general configurations (e.g. pidfile/socket location, user ID, etc.). Within the global context is the 'server' section which houses an arbitrary number of 'minecraft' blocks, each containing a different Minecraft server's configuration. 

PyMine's one-to-many control semantics are inspired by <a href='http://docs.ansible.com/'>Ansible</a>. PyMine allows you to send commands to a default server, specified in the config file, or to have your commands out to all Minecraft servers whose name matches a give regular regular expression. To broadcast a command, simply enter you command, followed by a right-facing chevron (>) and your regular expression.

\>\>\> weather rain # Changes the weather to rain on the default server<br>
\>\>\> kill Bob > \*creative # Kills all Bobs on servers ending in 'creative'<br>
\>\>\> say I AM BECOME DEATH > all # Syntactic sugar for .\*<br>

PyMine can be executed two ways - either as a command line one-off or as an interactive session. To enter into an interactive session simply excecute PyMine with no additional arguments. To use it as one-off execute PyMine followed by your command.

Beyond the small set of control keywords (start|stop|restart|status|backup) communication with the Minecraft server via PyMine is completely transparent. This allows for awesomeness such as:

$ pymine start<br>
$ pymine weather rain<br>
$ pymine weather clear<br>
$ pymine time set 6000<br>
$ pymine say STOP HITTING YOURSELF!<br>
$ pymine stop

A systemd service file has been included for hook-ups into the init system.

$ sudo ln -s pymine /usr/bin/pymine<br>
$ sudo mv pymine.service /usr/lib/systemd/system<br>
$ sudo systemctl enable pymine<br>
$ sudo systemctl start pymine<br>

<p><strong>Dependencies:</strong><br>
python-daemon<br>
pyyaml<br>
psutils<br></p>

<p><strong>Python Version:</strong><br>
Python >= 2.7
