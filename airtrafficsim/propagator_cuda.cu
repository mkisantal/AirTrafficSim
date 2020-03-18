#include <math.h>

#define DEG2RAD 0.0174532925
#define RAD2DEG 57.2957795
#define FT_PER_MIN_TO_M_PER_SEC 0.00508

// nvcc -Xcompiler -fPIC -shared propagator_cuda.cu -o propagator_cuda.so


__device__
inline size_t idx(size_t i, size_t y, size_t vec_len=3){

    /* The numpy vectors are flattened for some reason. This fcn gives the correct index. */

    return i*vec_len + y;
}


__global__
void propagate(int n, float *position, float *velocity, float dt,
               float *turn_rate, float *climb_rate, float *heading){
    
    int index = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = blockDim.x * gridDim.x;
        
    for (int i = index; i < n; i += stride){
        float horizontal_speed = sqrt(velocity[idx(i,0)]*velocity[idx(i,0)] + 
                                    velocity[idx(i,1)]*velocity[idx(i,1)]);
        heading[i] = atan2(velocity[idx(i,1)], velocity[idx(i,0)])
                                    + turn_rate[i] * dt * DEG2RAD;

        velocity[idx(i, 0)] = cos(heading[i]) * horizontal_speed;
        velocity[idx(i, 1)] = sin(heading[i]) * horizontal_speed;
        velocity[idx(i, 2)] = climb_rate[i] * FT_PER_MIN_TO_M_PER_SEC;

        position[idx(i, 0)] += velocity[idx(i, 0)] * dt;
        position[idx(i, 1)] += velocity[idx(i, 1)] * dt;
        position[idx(i, 2)] += velocity[idx(i, 2)] * dt;
    }
}


extern "C" void propagate_cuda(float *position,
                               float *velocity,
                               float dt,
                               float *turn_rate,
                               float *climb_rate,
                               float *heading,
                               int fleet_size){
    
    float *d_position, *d_velocity, *d_turn_rate, *d_climb_rate, *d_heading;
    
    cudaMalloc(&d_position, fleet_size*3*sizeof(float));
    cudaMalloc(&d_velocity, fleet_size*3*sizeof(float));
    cudaMalloc(&d_turn_rate, fleet_size*sizeof(float));
    cudaMalloc(&d_climb_rate, fleet_size*sizeof(float));
    cudaMalloc(&d_heading, fleet_size*sizeof(float));
    
    cudaMemcpy(d_position, position, fleet_size*3*sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_velocity, velocity, fleet_size*3*sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_turn_rate, turn_rate, fleet_size*sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_climb_rate, climb_rate, fleet_size*sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_heading, heading, fleet_size*sizeof(float), cudaMemcpyHostToDevice);


    propagate<<<1, 1>>>(fleet_size, d_position, d_velocity, dt, d_turn_rate,
                        d_climb_rate, d_heading); 

    cudaDeviceSynchronize();
        
    cudaMemcpy(position, d_position, fleet_size*3*sizeof(float), cudaMemcpyDeviceToHost);
    cudaMemcpy(velocity, d_velocity, fleet_size*3*sizeof(float), cudaMemcpyDeviceToHost);
    cudaMemcpy(turn_rate, d_turn_rate, fleet_size*sizeof(float), cudaMemcpyDeviceToHost);
    cudaMemcpy(climb_rate, d_climb_rate, fleet_size*sizeof(float), cudaMemcpyDeviceToHost);
    cudaMemcpy(heading, d_heading, fleet_size*sizeof(float), cudaMemcpyDeviceToHost);
    
    cudaFree(position);
    cudaFree(velocity);
    cudaFree(turn_rate);
    cudaFree(climb_rate);
    cudaFree(heading); 
    return;
}
