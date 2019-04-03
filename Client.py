import utils.py

class Client(DHT_Client):
	def __init__(self, address, ClientID):
		DHT_Client.__init__(address)
		self.ClientID = ClientID
        self.logger = logging.getLogger('Client')

    def request(self, key, value):
    	#Quando chama o metodo request vai fazer um put no recepcionista, 
    	#o value vem como dicionario de pedido
        super().put(RECEPTIONIST_ID, value)

    def receive(self, key):
       	#Quando da receive vai fazer um get do empregado
       	super().get(EMPLOYEE_ID)