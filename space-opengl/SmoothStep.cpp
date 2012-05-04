#include "SmoothStep.h"

#include <iostream>

SmoothStep::SmoothStep(int n, const double initial[], double length_millis) {
    this->n = n;
    pos = new double[n];
    start = new double[n];
    dest = new double[n];
    array_copy(initial, pos);
    array_copy(initial, start);
    array_copy(initial, dest);
    this->length_millis = length_millis;
    time_millis = 0;
}

double *SmoothStep::get() {
    return pos;
}

void SmoothStep::set(const double dest[]) {
    // only animate if this is a new dest
    if (not array_equal(dest, this->dest)) {
        array_copy(dest, this->dest);
        array_copy(pos, start);
        time_millis = 0;
    }
}

void SmoothStep::set_now(double dest[]) {
    time_millis = 0;
    array_copy(dest, this->dest);
    array_copy(dest, start);
    array_copy(dest, pos);
}

bool SmoothStep::is_finished() {
    return array_equal(start, dest);
}

void SmoothStep::update(double millis) {
    if (not is_finished()) {
        time_millis += millis;
        if (time_millis >= length_millis) {
            time_millis = 0;
            array_copy(dest, pos);
            array_copy(dest, start);
        }
        double step = time_millis / length_millis;
        step = step * step * (3 - 2 * step); // smoothstep
        for (int i = 0; i < n; i++) {
            pos[i] = dest[i] * step + start[i] * (1 - step);
        }
    }
}

void SmoothStep::array_copy(const double source_a[], double dest_a[]) {
    for (int i = 0; i < n; i++) {
        dest_a[i] = source_a[i];
    }
}

bool SmoothStep::array_equal(const double a[], const double b[]) {
    for (int i = 0; i < n; i++) {
        if (a[i] != b[i]) {
            return false;
        }
    }
    return true;
}

SmoothStep::~SmoothStep() {
    delete[] pos;
    delete[] start;
    delete[] dest;
}
