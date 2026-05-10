module branch(
    input  [31:0] a,
    input  [31:0] b,
    input  [3:0] fn,
    output reg taken
);

always @(*) begin
    case (fn)
        4'h0: taken = 0;
        4'h1: taken = (a == b);
        4'h2: taken = (a <  b);
        4'h3: taken = (a <= b);

        4'h5: taken = (a == 32'd0);
        4'h6: taken = (a <  32'd0);
        4'h7: taken = (a <= 32'd0);

        4'h8: taken = 1;
        4'h9: taken = (a != b);
        4'hA: taken = (a >= b);
        4'hB: taken = (a >  b);

        4'hD: taken = (a != 32'd0);
        4'hE: taken = (a >= 32'd0);
        4'hF: taken = (a >  32'd0);

        default: taken = 0;
    endcase
end

endmodule
