int complex_algorithm(int start_val, int threshold) {
    int accumulator = 0;
    int multiplier = 1;

    if (start_val < 0) {
        start_val = start_val * -1;
    }

    while (accumulator < threshold) {
        if (start_val % 2 == 0) {
            accumulator = accumulator + (start_val * multiplier);
            multiplier = multiplier * 2;
        } else {
            accumulator = accumulator + start_val;
        }
        
        start_val = start_val - 1;
        
        if (start_val == 0) {
            break;
        }
    }

    int final_result = accumulator - multiplier;
    return final_result;
}