#include "game.h"
#include "RockEntity.h"
#include <iostream>
#include <GL/glut.h>
#include <cstdlib>
#include <cmath>

Game::Game(int width, int height) {
    left = 0; top = 0, zoom = 1;
    this->width = width;
    this->height = height;
    
    // create some rocks
    for (int i = 0; i < 10; i++) {
        int x = rand() % 400;
        int y = rand() % 400;
        entities.push_back(new RockEntity(this, x, y));
    }
    
    // create ship
    ship = new ShipEntity(this);
    entities.push_back(ship);
    
    // init opengl
    glEnable(GL_TEXTURE_2D);
	glEnable(GL_BLEND);
	glEnableClientState(GL_VERTEX_ARRAY);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glViewport(0, 0, width, height);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	glOrtho(0.0, width, height, 0.0, -1.0f, 1.0f);
}

void Game::update(double millis) {
    // update entities
    for (unsigned int i = 0; i < entities.size(); i++) {
        GameEntity *e = entities.at(i);
        e->update(millis);
    }
    
    // center the view
    double cx = ship->pos[0]; double cy = ship->pos[1];
    grid_to_px(&cx, &cy);
    cx -= width/2; cy -= height/2;
    px_to_grid(&cx, &cy);
    left = cx; top = cy;
    
}

void Game::draw() {
    // clear screen
    glClear(GL_COLOR_BUFFER_BIT);
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();
	
	// draw background
	draw_star_layer(10, 0.3);
	draw_star_layer(2, 0.5);
	draw_star_layer(1, 1.0);
	
	// draw entities
	for (unsigned int i = 0; i < entities.size(); i++) {
        GameEntity *e = entities.at(i);
        e->draw();
    }
}

void Game::draw_star_layer(double parallax, double brightness) {
    const int size = 256; // size of tile in grid units
    const int stars = 64; // stars per tile
    
    // parallax adjusted left, top coords
    double l = left / parallax;
    double t = top / parallax;
	
	int first_x = ((int)l / size * size) - size; // HACK: added -size
	int first_y = ((int)t / size * size) - size;
	int last_x = (int)(l + width / zoom) / size * size;
	int last_y = (int)(t + height / zoom) / size * size;
	//std::cout << "x " << first_x << " to " << last_x << std::endl;
	for (int x = first_x; x <= last_x; x += size) {
	    for (int y = first_y; y <= last_y; y += size) {
	        double px = x, py = y;
	        // parallax version of grid_to_px 
	        px = (px - l) * zoom;
            py = (py - t) * zoom;
	        // draw
	        //GLfloat verts[8] = {0,0,1,0,1,1,0,1};
	        GLfloat verts[stars*2];
	        srand(x*3+y*5+parallax*7); // seed with poor man's hash
	        for (int i = 0; i < stars; i++) {
	            verts[i*2] = (float) rand() / RAND_MAX;
	            verts[i*2+1] = (float) rand() / RAND_MAX;
	        }
            glPushMatrix();
	        glColor4f(brightness, brightness, brightness, 1.0f);
	        glVertexPointer(2, GL_FLOAT, 0, verts);
	        glTranslatef(px, py, 0);
	        glScalef(size*zoom, size*zoom, 0);
	        glDrawArrays(GL_POINTS, 0, stars);
	        glPopMatrix();
	    }
	}
}

void Game::event(event_t type, unsigned char key) {
    //std::cout << "game: got key event for " << key << std::endl;
    if (type == KEYUP or type == KEYDOWN) {
        switch (key) {
            case 'w':
                ship->thrust = (KEYDOWN == type);
                break;
            case 'a':
                ship->rotate_left = (KEYDOWN == type);
                break;
            case 'd':
                ship->rotate_right = (KEYDOWN == type);
                break;
            case ' ':
                ship->shoot = (KEYDOWN == type);
                break;
            case 'z':
                zoom += 0.1;
                break;
            case 'x':
                zoom -= 0.1;
                break;
            
        }
    }
}

void Game::grid_to_px(double *x, double *y) {
    *x = (*x - left) * zoom;
    *y = (*y - top) * zoom;
}

void Game::px_to_grid(double *x, double *y) {
    *x = left + (*x / zoom);
    *y = top + (*y / zoom);
}
