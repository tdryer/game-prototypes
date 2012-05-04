SOURCES = main.cpp game.cpp SmoothStep.cpp GameEntity.cpp RockEntity.cpp ShipEntity.cpp
OBJECTS = $(SOURCES:.cpp=.o)
EXECUTABLE = main

CPP = g++
CPPFLAGS = -Wall -g
LD = g++
LDFLAGS = -lglut -lGLU

all: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
	$(LD) $(OBJECTS) $(LDFLAGS) -o $@

.cpp.o:
	$(CPP) $(CPPFLAGS) -c $< -o $@

clean:
	rm -f *.o $(EXECUTABLE)

