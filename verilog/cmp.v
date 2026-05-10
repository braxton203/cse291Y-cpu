module cmp(
    input [31:0] a,
    input [31:0] b,
    input [3:0] fn,
    output reg [31:0] result
);

always @(*) begin
    case (fn)
        4'h0: result = 32'd0;                         // F
        4'h1: result = (a == b) ? 32'd1 : 32'd0;      // EQ
        4'h2: result = (a <  b) ? 32'd1 : 32'd0;      // LT
        4'h3: result = (a <= b) ? 32'd1 : 32'd0;      // LTE
        4'h8: result = 32'd1;                         // T
        4'h9: result = (a != b) ? 32'd1 : 32'd0;      // NE
        4'hA: result = (a >= b) ? 32'd1 : 32'd0;      // GTE
        4'hB: result = (a >  b) ? 32'd1 : 32'd0;      // GT
        default: result = 32'd0;
    endcase
end

endmodule