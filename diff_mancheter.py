import matplotlib.pyplot as plt

def differential_manchester_encode(bit_string, save_path="diffmanchester_signal.png"):
    if not all(bit in "01" for bit in bit_string):
        raise ValueError("Input must contain only 0s and 1s")

    time = []
    signal = []

    t = 0
    current_level = 1 

    for bit in bit_string:
        
        if bit == '0':
            current_level *= -1 
        
        time.extend([t, t + 0.5])
        signal.extend([current_level, current_level])

        current_level *= -1

        time.extend([t + 0.5, t + 1])
        signal.extend([current_level, current_level])

        t += 1

    # Plot
    plt.figure()
    plt.step(time, signal, where='post')
    plt.ylim(-2, 2)
    plt.yticks([-1, 1])
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.title(f"Differential Manchester Encoding for Data = {bit_string}")
    plt.grid(True)

    plt.savefig(save_path)
    plt.show()

    print(f"Image saved as {save_path}")


while True:
    data = input("\nEnter binary data (or type 'exit' to quit): ")

    if data.lower() == "exit":
        print("Exiting program...")
        break

    try:
        differential_manchester_encode(data)
    except ValueError as e:
        print("Error:", e)