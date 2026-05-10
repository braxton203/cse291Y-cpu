module alu(
    input  [31:0] a,
    input  [31:0] b,
    input  [3:0] fn,
    output reg [31:0] result
);

always @(*) begin
    case (fn)
        4'h0: result = a + b;
        4'h1: result = a - b;
        4'h4: result = a & b;
        4'h5: result = a | b;
        4'h6: result = a ^ b;
        4'hC: result = ~(a & b);
        4'hD: result = ~(a | b);
        4'hE: result = ~(a ^ b);
        default: result = 32'd0;
    endcase
end

endmodule