tgz:
	tar -cvzf soares.tgz planetwars \
		__init__.py MyBot.py bot.py \
		universe.py planet.py fleet.py \
		action.py lock.py

clean:
	rm -f bot.tgz
