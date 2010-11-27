tgz:
	tar -cvzf soares.tgz planetwars \
		__init__.py MyBot.py bot.py \
		universe.py planet.py fleet.py \
		action.py contract.py \
		weight.py exception.py

clean:
	rm -f bot.tgz
