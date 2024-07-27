#!/usr/bin/python3
import RPi.GPIO as GPIO
import time

class StepperMotor:
    def __init__(self, in1, in2, in3, in4):
        """
       Inizializza un oggetto StepperMotor con i pin GPIO specificati.

       :param in1: Pin GPIO per il primo input del motore.
       :param in2: Pin GPIO per il secondo input del motore.
       :param in3: Pin GPIO per il terzo input del motore.
       :param in4: Pin GPIO per il quarto input del motore.
       :param steps_per_revolution: numero di steps per una rivoluzione completa
       """
        # Definizione dei pin GPIO
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4

        # Il motore avanza di un passo ad ogni cambiamento nella sequenza. 
        # Utilizza tutta la corrente in ogni fase per avere massima coppia.
        self.step_sequence = [
            [1, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 1],
            [1, 0, 0, 1]
        ]
        
        # Steps per revolution
        self.steps_per_revolution = len(self.step_sequence)*512

        # Configurazione GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.in3, GPIO.OUT)
        GPIO.setup(self.in4, GPIO.OUT)

        # Inizializzazione dei pin
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.LOW)

        self.motor_pins = [self.in1, self.in2, self.in3, self.in4]
    
    def cleanup(self):
        """
        Pulisce la configurazione dei pin GPIO, impostandoli a LOW e liberando le risorse.
        """
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.LOW)
        GPIO.cleanup()

    def move(self, gradi=None, rpm=15, direction=1, time_limit=None, door_sensor=None):
        """
        Muove il motore passo-passo di un numero specificato di passi alla velocità indicata.

        :param gradi: Gradi di rotazione. Se None, il motore ruota all'infinito.
        :param rpm: Velocità di rotazione in rivoluzioni per minuto. MIN = 0.1, MAX = 18. Valori fuori range vengono settati ai valori limite.
        :param direction: Direzione della rotazione. 1 per senso orario, -1 per senso antiorario.
        :param time_limit: Tempo massimo in secondi. Se None, non c'è limite di tempo.
        :param door_sensor: oggetto DoorSensor che interrompe il movimento
        """
        
        # Controllo se entrambi i parametri sono None
        if gradi is None and time_limit is None:
            raise ValueError("Necessario definire almeno gradi o time_limit")
            return
        
        # Calcola il numero di passi se i gradi sono specificati
        if gradi is not None:
            steps_per_degree = self.steps_per_revolution / 360
            total_steps = int(abs(gradi) * steps_per_degree)
        else:
            total_steps = None

        # Impostare la direzione
        if direction not in (-1, 1):
            raise ValueError("Direzione invalida")
            return
        
        # Limitazione della velocità entro i limiti
        if rpm > 18:
            rpm = 18
        elif rpm < 0.1:
            rpm = 0.1
        
        # Calcolo del tempo di pausa
        step_sleep = 60 / (rpm * self.steps_per_revolution / len(self.step_sequence))
    
        motor_step_counter = 0
        start_time = time.time()
        try:
            while total_steps is None or total_steps > 0:
                # Controlla lo stato del sensore di porta
                if door_sensor is not None and door_sensor.get_state() == False:
                    print("Switch magnetico attivato")
                    break
                
                # Impostare i pin in base alla sequenza di passi
                for pin in range(4):
                    GPIO.output(self.motor_pins[pin], self.step_sequence[motor_step_counter][pin])
                
                # Aggiornare il contatore dei passi
                motor_step_counter = (motor_step_counter - direction) % len(self.step_sequence)
                
                # Pausa tra i passi che determina la velocita
                time.sleep(step_sleep)
                
                # Decrementa total_steps se non è infinito
                if total_steps is not None:
                    total_steps -= 1
                
                # Verifica se è trascorso il tempo massimo
                if time_limit is not None and (time.time() - start_time) > time_limit:
                    print("Tempo massimo raggiunto")
                    return

        except KeyboardInterrupt:
            return
        
class DoorSensor:
    def __init__(self, pin):
        """
        Inizializza un oggetto DoorSensor.

        :param pin: Il numero del pin GPIO a cui è collegato il sensore.
        """
        self.pin = pin
        
        # Configura i GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def get_state(self):
        """
        Restituisce lo stato attuale del sensore della porta.

        :return: True se la porta è aperta, False se è chiusa.
        """
        return GPIO.input(self.pin) == GPIO.HIGH

    def cleanup(self):
        """
        Pulisce la configurazione GPIO.
        """
        GPIO.cleanup()
