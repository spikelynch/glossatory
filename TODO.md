TODO
====

More efficient use of CPU: only run the neural net once a day and harvest the other results from that run.

- first crontab entry: run as normal
- rest of the day: find the most recent log, and treat it as a textfile - so we get the first n entries from the same run

The frequency can be changed. Also, if the neural net doesn't run, we'll keep reading the most recent file

- need to coordinate this with how the oulipo harvester works

Build the functionality into rnnbot.py so that it works in all of the RNN bots

- note that this will get boring if alliteration is turned on - maybe leave it off for a while

[BELOW VVVV DONE]

Currently on the webfaction server, the existing RNN bots are using the master version of glossatory which doesn't rely on rnnbot.py.

The only bot using the new cleaner structure is gravidum_cor, the Anatomy of Melancholy bot.

At some stage, the other RNN bots need to be ported:

* glossatory
* oulipo_excavate
* oulipo_live
* vulgar

Note that glossatory, oulipo_live and vulgar all used the same codebase, the old version of glossatory