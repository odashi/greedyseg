# makefile
CXX=g++
CFLAGS=-std=c++11 -O3 -Wall -Werror -fopenmp

OBJS_SPLIT_GDP=split_gdp.o



all:
	@echo "USAGE: make split_gdp"

clean:
	$(RM) *.o split_gdp

split_gdp: $(OBJS_SPLIT_GDP)
	$(CXX) $(CFLAGS) -o split_gdp $(OBJS_SPLIT_GDP) 


.cpp.o:
	$(CXX) $(CFLAGS) -c -o $@ $<



split_gdp.o: 

