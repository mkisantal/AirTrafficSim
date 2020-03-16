#include <math.h>
#include <iostream>
#include <iostream>

#define DEG2RAD 0.0174532925
#define RAD2DEG 57.2957795
#define FT_PER_MIN_TO_M_PER_SEC 0.00508

// clang++ -Wall -fPIC -shared propagator.cpp -o propagator.so


size_t idx(size_t i, size_t y, size_t vec_len=3){

	/* The numpy vectors are flattened for some reason. This fcn gives the correct index. */

	return i*vec_len + y;
}


extern "C" void propagate(float *position, float *velocity, float dt, float turn_rate, float climb_rate, float *heading){

	/* Propagate single aircraft in simulation. */

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


extern "C" void propagate_fleet(float *position, float *velocity, float dt, float *turn_rate,
								float *climb_rate, float *heading, int fleet_size){

	/* Propagating multiple aircraft simultaneously. Inputs are flattened 2D numpy arrays */

	for (int i=0; i<fleet_size; i++){

		float horizontal_speed = sqrt(velocity[idx(i,0)]*velocity[idx(i,0)] + velocity[idx(i,1)]*velocity[idx(i,1)]);
		heading[i] = atan2(velocity[idx(i,1)], velocity[idx(i,0)]) + turn_rate[i] * dt * DEG2RAD;

		velocity[idx(i, 0)] = cos(heading[i]) * horizontal_speed;
		velocity[idx(i, 1)] = sin(heading[i]) * horizontal_speed;
		velocity[idx(i, 2)] = climb_rate[i] * FT_PER_MIN_TO_M_PER_SEC;

		position[idx(i, 0)] += velocity[idx(i, 0)] * dt;
		position[idx(i, 1)] += velocity[idx(i, 1)] * dt;
		position[idx(i, 2)] += velocity[idx(i, 2)] * dt;
	}

	return;

}
