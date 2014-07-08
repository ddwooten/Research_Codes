# Creator: Daniel Wooten
# Version 1.0.
""" SERP_mat_conditioner is a simple python script that takes in a tab delimited input
    file which contains parameters and options and outputs the appropriate fuel
    composition in atomic percent inside of a SERPENT file that is also specified in the
    input file. A sample input file is given below
    <<
    < Combined/Seperate >
    < Free/Preserved >
    < Path_to_SERPENT_input_file.txt >
    < A of isotope n , Z of n , < C , A , F , H >, BNC , BNH , Abudance >
    >>
    The < CAFH > flag determines how the < Abundance > value is handled. This will be
    made more clear in the body of the code through comments and doc strings """


