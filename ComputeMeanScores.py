import os
import argparse

def process_output_files(output_folder, report_file):
    summary_data = []

    for output_file in os.listdir(output_folder):
        if not output_file.endswith(".txt"):
            continue  

        file_path = os.path.join(output_folder, output_file)
        run_name = output_file.split("_")[0] 

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

                lines = lines[1:]

                if not lines or "bad format" in lines[0]:
                    summary_data.append([run_name, "bad format", "bad format", "bad format", "bad format"])
                else:
                    sum_ap, sum_p10, sum_ndcg10, sum_ndcg1000 = 0.0, 0.0, 0.0, 0.0
                    count = 0

                    for line in lines:
                        parts = line.strip().split(",")
                        if len(parts) != 5:
                            continue  

                        try:
                            ap = float(parts[1])
                            p10 = float(parts[2])
                            ndcg10 = float(parts[3])
                            ndcg1000 = float(parts[4])

                            sum_ap += ap
                            sum_p10 += p10
                            sum_ndcg10 += ndcg10
                            sum_ndcg1000 += ndcg1000
                            count += 1
                        except ValueError:
                            continue  
                    if count > 0:
                        mean_ap = round(sum_ap / count, 3)
                        mean_p10 = round(sum_p10 / count, 3)
                        mean_ndcg10 = round(sum_ndcg10 / count, 3)
                        mean_ndcg1000 = round(sum_ndcg1000 / count, 3)
                        summary_data.append([run_name, mean_ap, mean_p10, mean_ndcg10, mean_ndcg1000])
                    else:
                        summary_data.append([run_name, "bad format", "bad format", "bad format", "bad format"])
        except Exception as e:
            print(f"Error processing file {output_file}: {e}")
            summary_data.append([run_name, "bad format", "bad format", "bad format", "bad format"])

    with open(report_file, 'w') as f:
        f.write("Run Name,Mean Average Precision,Mean P@10,Mean NDCG@10,Mean NDCG@1000\n")
        for row in summary_data:
            f.write(",".join(map(str, row)) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process output files to generate a summary report.")
    parser.add_argument("output_folder", type=str, help="Path to the folder containing output files")
    parser.add_argument("report_file", type=str, help="Path to the output report file")

    args = parser.parse_args()

    process_output_files(args.output_folder, args.report_file)
