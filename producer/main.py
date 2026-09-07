#from generator import generate_vote
#from kafka_producer import send_vote

#import random
#import time

#MIN_DELAY = 0.5
#MAX_DELAY = 2

#print("=" * 60)
#print("      Générateur de votes démarré")
#print("=" * 60)

#nb_votes = 0

#while True:

#    vote = generate_vote()

#    send_vote(vote)

#    nb_votes += 1

#    print(f"Total votes envoyés : {nb_votes}")

 #   time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

from generator import generate_vote
from kafka_producer import send_vote

import time

DELAY = 5 # secondes

print("=" * 60)
print("      Générateur de votes démarré")
print("=" * 60)

nb_votes = 0

while True:

    vote = generate_vote()

    send_vote(vote)

    nb_votes += 1

    print(f"Total votes envoyés : {nb_votes}")

    time.sleep(DELAY)