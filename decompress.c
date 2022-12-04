// Example decompression function
// Pass a block_map and a block_list and this will write to the OLED
static void oled_write_compressed_P(compressed_oled_frame_t frame) {
    uint16_t block_index = 0;
    for (uint16_t i=0; i<frame.data_len; i++) {
        uint8_t bit = i%8;
        uint8_t map_index = i/8;
        uint8_t _block_map = (uint8_t)pgm_read_byte_near(frame.block_map + map_index);
        uint8_t nonzero_byte = (_block_map & (1 << bit));
        if (nonzero_byte) {
            const char data = (const char)pgm_read_byte_near(frame.block_list + block_index++);
            oled_write_raw_byte(data, i);
        } else {
            const char data = (const char)0x00;
            oled_write_raw_byte(data, i);
        }
    }
}
