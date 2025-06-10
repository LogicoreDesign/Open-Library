/* -Register module
    Updates data on the posedge of the clk_i or the arst_i signal.
*/
`include "timescale.vs"

module Reg #(
    parameter integer DATA_W  = 1,
    parameter integer RST_VAL = {DATA_W{1'b0}}
) (
    `include "io_clk_en_rst.vs"
    input  wire              data_e,
    input  wire              data_r,
    input  wire [DATA_W-1:0] data_n,
    output reg  [DATA_W-1:0] data_q
);

  `include "reg_data_q.vs" // , , _r, _e,

endmodule
