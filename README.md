# Drive-Through Restaurant P2P

## Prerequisites

* Clone this repository

## What to do next
	Junçao:
		Ligam-se todos ao restaurante
		Passar mensagem com o dicionario com os ID's das entidades
		Passar 2 vezes a mensagem

	Discovery:
		--
		--

	Processo de receber token:
		1. UDP
		2. Check if ID da MSG == NodeID (else go to 5.)
		3. Guardar a mensagem na queue in
		4. Ver se queueOut > 0 e enviar a mensagem no queue out
		5. Passa token a sucessor

## How to run
Open two terminals:

restaurant:
```console
$ python restaurant.py
```
client:
```console
$ python client.py
```

## Git Upstream

Keep your fork sync with the upstream

```console
$ git remote add upstream git@github.com:mariolpantunes/restaurant-p2p.git
$ git pull upstream master
```

## Authors

* **Mário Antunes** - [mariolpantunes](https://github.com/mariolpantunes)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
