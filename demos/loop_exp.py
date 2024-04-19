from dallinger.experiments import Griduniverse
import random

experiment = Griduniverse()
participants = 2
iterations = 1


for i in range(iterations):
    app_name = "dlgr-lucasl-" + str(i)
    others = random.choice([True, False])
    chat = random.choice([True, False])

    while(other == True and chat == False):  
        others = random.choice([True,False])
        chat = random.choice([True, False])
    data = experiment.run(
        mode="sandbox",
        max_participants=participants,
        num_dynos_worker=participants,
        others_visible=others,
        show_chatroom=chat,
        id=app_name,
    )
    filename = "DataTrial" + str(i)
    filename += ".csv"
    experiment.save_data_to_file(data, filename)
    

print(
    "Script successfully ran with %d participants for %d iterations"
    % (participants, iterations)
)
