#include <math.h>
#include <iostream>
#include <iostream>

#define DEG2RAD 0.0174532925
#define RAD2DEG 57.2957795
#define FT_PER_MIN_TO_M_PER_SEC 0.00508

// clang++ -Wall -fPIC -shared propagator.cpp -o propagator.so


extern "C" void propagate(float *position, float *velocity, float dt, float turn_rate, float climb_rate, float *heading){

	// update heading
	float horizontal_speed = sqrt(velocity[0]*velocity[0] + velocity[1]*velocity[1]);
	*heading = atan2(velocity[1], velocity[0]) + turn_rate * dt * DEG2RAD;

	// calculate velocity
	velocity[0] = cos(*heading) * horizontal_speed;
	velocity[1] = sin(*heading) * horizontal_speed;
	velocity[2] = climb_rate * FT_PER_MIN_TO_M_PER_SEC;

	// calculate position
	position[0] += velocity[0] * dt;
	position[1] += velocity[1] * dt;
	position[2] += velocity[2] * dt;

	return;

}