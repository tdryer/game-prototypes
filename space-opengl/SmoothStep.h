#ifndef SMOOTHSTEP_H
#define SMOOTHSTEP_H

//TODO: add const

class SmoothStep {
public:
    SmoothStep(int n, const double initial[], double length_millis);
    ~SmoothStep();
    double *get();
    void set(const double dest[]);
    void set_now(double dest[]);
    bool is_finished();
    void update(double millis);
private:
    int n;
    double *pos, *start, *dest, length_millis, time_millis;
    void array_copy(const double source_a[], double dest_a[]);
    bool array_equal(const double a[], const double b[]);
};

#endif
