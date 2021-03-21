// Example decompression function
// Pass a block_map and a block_list and this will write to the OLED

static void oled_write_compressed_P(const char* input_block_map, const char* input_block_list) { //Inflate and write a frame to the OLED
    uint16_t block_index = 0;
    for (uint16_t i=0; i<NUM_OLED_BYTES; i++) {
        uint8_t bit = i%8;
        uint8_t map_index = i/8;
        uint8_t _block_map = (uint8_t)pgm_read_byte_near(input_block_map + map_index);
        // uprintf("i: %u bit: %u map_index: %u _block_map: 0x%02X ", i, bit, map_index, _block_map);
        uint8_t nonzero_byte = (_block_map & (1 << bit));
        if (nonzero_byte) {
            const char data = (const char)pgm_read_byte_near(input_block_list + block_index++);
            oled_write_raw_byte(data, i);
            // uprintf("inf: %u block_index: %u data: 0x%02X\n", nonzero_byte, block_index-1, data);
        } else {
            const char data = (const char)0x00;
            oled_write_raw_byte(data, i);
            // uprintf("inf: %u block_index: %u data: 0x%02X\n", nonzero_byte, block_index-1, data);
        }
        // wait_us(30000);
    }
}