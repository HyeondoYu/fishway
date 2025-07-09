def handle_command(command):
    print(f"[Control Command Receive] {command}")
    
    if command == "left":
        print("move left")
    elif command == "right":
        print("move right")
