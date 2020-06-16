
#takes a list of options as input which will be printed as a numerical list
#Also optionally takes messages as input to be printed after the options but before input request
#Ultimately the users choice is returned
def selector(options,*messages):
    rego = 'y'
    while rego.lower() == "y":
        n=1
        for x in options:
            print(str(n) + ". " + str(x))
            n = n + 1
        n=1

        print("")
        for arg in messages:
            print(arg)

        choice = input( " :> ")
        if choice == "":
            return False

        try:
            i_choice = int(choice)
            assert isinstance(i_choice, int)
        except AssertionError:
            print("\nError: Sorry, that's not a valid entry, please enter a number from the list")
            rego = input("Would you like to try again? Type Y for yes or N for no :> ")
            if rego.lower() == "y":
                pass
            else:
                break

        print("")
        p=1
        for x in options:
            if int(choice) == p:
                value = x
            p = p + 1
        p=1

        if value in options:
            return value
        else:
            if not value:
                print("\nError: Sorry, that's not a valid entry, please enter a number from the list")
                rego = input("Would you like to try again? Type Y for yes or N for no :> ")
    return False
