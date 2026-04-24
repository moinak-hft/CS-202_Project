import subprocess

def dot_to_png(dot_file, output_file):
    subprocess.run(["dot", "-Tpng", dot_file, "-o", output_file])
    print(f"Generated {output_file}")

dot_to_png("cfg.dot", "cfg.png")