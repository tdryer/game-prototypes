#include <iostream>
#include <fstream>
#include <queue>
#include <GL/glut.h>

#include "game.h"

using namespace std;

Game* g;

void handleMouseMove(int x, int y) {
    
}

void keyboard_up(unsigned char key, int x, int y) {
    g->event(KEYUP, key);
}

void keyboard_down(unsigned char key, int x, int y) {
    g->event(KEYDOWN, key);
}

void handleResize(int w, int h) {
    /*
    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(45.0, (double)w/(double)h, 1.0, 200.0);
    */
}

void drawScene() {
    g->draw();
    
    glutSwapBuffers();
}

int last_update = 0;
const int TARGET_DELAY = 1000 / 60; // 60 fps

void update(int val) {

    glutTimerFunc(16.67, update, 0);

    int this_update = glutGet(GLUT_ELAPSED_TIME);
    int elapsed_millis = this_update - last_update;
    last_update = this_update;
    
    /*
    int delay = TARGET_DELAY - elapsed_millis;
    if (delay < 0) {
        delay = 0;
    }
    */

    g->update(elapsed_millis);
    
    glutPostRedisplay();
    //glutTimerFunc(delay, update, 0);
}


int main(int argc, char** argv) {
    
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowSize(800, 600);
    glutCreateWindow("Tom's OpenGL demo");
    glutDisplayFunc(drawScene);
    
    glutIgnoreKeyRepeat(1);
    glutKeyboardFunc(keyboard_down);
    glutKeyboardUpFunc(keyboard_up);
    
    glutReshapeFunc(handleResize);
    glutPassiveMotionFunc(handleMouseMove);
    glutTimerFunc(0, update, 0);
    
    g = new Game(800, 600);
    
    glutMainLoop();
    return 0;
}
