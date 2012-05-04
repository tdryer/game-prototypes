#include "GameEntity.h"
#include "game.h"

#include <GL/glut.h>
#include <iostream>
#include <cmath>

GameEntity::GameEntity(Game *game) {
    this->game = game;

    pos[0] = 1.0;
    pos[1] = 1.0;
    v[0] = 0.0;
    v[1] = 0.0;
    r = 0.0;
    rs = 0;
    age = 0.0;
    radius = 1;
}

void GameEntity::update(double millis) {
    // calc position from velocity
    double dp[2] = {v[0] * (millis / 1000), v[1] * (millis / 1000)};
    pos[0] = pos[0] + dp[0];
    pos[1] = pos[1] + dp[1];
    
    age += millis;
    
    r += (rs * (millis / 1000));
}

// if entity is onscreen, calculate pixel position and call draw_local
void GameEntity::draw() {
    double x = pos[0];
    double y = pos[1];
    game->grid_to_px(&x, &y);
    if (x > 0 and x < game->width and y > 0 and y < game->height) {
        draw_local(x, y, game->zoom);
    }
}

void GameEntity::draw_local(double px, double py, double zoom) {
    GLfloat box_verts[8] = {-0.5,-0.5,0.5,-0.5,0.5,0.5,-0.5,0.5};
    glPushMatrix();
	glColor4f(1.0f, 1.0f, 1.0f, 1.0f);
	glVertexPointer(2, GL_FLOAT, 0, box_verts);
	
	
	
	glTranslatef(px, py, 0);
	glScalef(10*zoom, 10*zoom, 0);
	
	glRotatef(r, 0, 0, 1);
	
	glDrawArrays(GL_LINE_LOOP, 0, 4);
	glPopMatrix();
}

// return entity in entity_list which has collided with this entity, or null
GameEntity * GameEntity::check_collision(std::vector<GameEntity *> *entity_list) {
    for (unsigned int i = 0; i < entity_list->size(); i++) {
        GameEntity *e = entity_list->at(i);
        double dist = sqrt(pow(e->pos[0] - pos[0], 2) + pow(e->pos[1] - pos[1], 2));
        if (dist < e->radius + radius) {
            return e;
        }
    }
    return NULL;
}
