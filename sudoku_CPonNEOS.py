import sys

def solve_with_NEOS(job_xml):
    import xmlrpc.client
    import time

    NEOS_HOST="www.neos-server.org"
    NEOS_PORT=3333

    neos = xmlrpc.client.Server("https://%s:%d" % (NEOS_HOST, NEOS_PORT))

    (jobNumber,password) = neos.submitJob(job_xml)

    status="Waiting"
    while status == "Running" or status=="Waiting":
      time.sleep(1)
      status = neos.getJobStatus(jobNumber, password)

    return neos.getFinalResults(jobNumber, password).data.decode('utf-8')

def prepare_NEOS_job(i_category, i_solver, i_email, str_Sudoku):

        job_template = "<document><category>%s</category><solver>%s</solver><inputMethod>AMPL</inputMethod>"\
                       "<priority>long</priority><email>%s</email><model><![CDATA[%s]]></model><data><![CDATA[%s]]></data>"\
                       "<commands><![CDATA[%s]]></commands><comments><![CDATA[%s]]></comments></document>"

        model = "\n" \
        "param hints{1..9, 1..9} default 0;\n" \
        "var x{1..9, 1..9, 1..9} binary;\n" \
        "minimize DummyObj;\n" \
        "#constraints\n" \
        "s.t. c_hints{i in 1..9, j in 1..9, k in 1..9: hints[i,j] = k}: x[i,j,k] = 1; # hints\n" \
        "s.t. c_cells{i in 1..9, j in 1..9}: sum{k in 1..9} x[i,j,k]  = 1; # cells\n" \
        "s.t. c_rows{i in 1..9, k in 1..9}: sum{j in 1..9} x[i,j,k]  = 1; # rows\n" \
        "s.t. c_columns{j in 1..9, k in 1..9}: sum{i in 1..9} x[i,j,k]  = 1; # columns\n" \
        "s.t. c_b1{k in 1..9}: sum{i in 1..3, j in 1..3} x[i,j,k]=1; # block 1\n" \
        "s.t. c_b2{k in 1..9}: sum{i in 1..3, j in 4..6} x[i,j,k]=1; # block 2\n" \
        "s.t. c_b3{k in 1..9}: sum{i in 1..3, j in 7..9} x[i,j,k]=1; # block 3\n" \
        "s.t. c_b4{k in 1..9}: sum{i in 4..6, j in 1..3} x[i,j,k]=1; # block 4\n" \
        "s.t. c_b5{k in 1..9}: sum{i in 4..6, j in 4..6} x[i,j,k]=1; # block 5\n" \
        "s.t. c_b6{k in 1..9}: sum{i in 4..6, j in 7..9} x[i,j,k]=1; # block 6\n" \
        "s.t. c_b7{k in 1..9}: sum{i in 7..9, j in 1..3} x[i,j,k]=1; # block 7\n" \
        "s.t. c_b8{k in 1..9}: sum{i in 7..9, j in 4..6} x[i,j,k]=1; # block 8\n" \
        "s.t. c_b9{k in 1..9}: sum{i in 7..9, j in 7..9} x[i,j,k]=1; # block 9\n" \

        data = "\n" \
        "param hints: 1 2 3 4 5 6 7 8 9 :=  \n" \

        for i in range(9):
            data = data + ('         ' + str(i+1) + '   ' + ' '.join(str_Sudoku[i * 9 : i*9 + 9])) + '\n'

        data = data + ';'

        commands = '\n' \
        'solve; \n' \
        'printf ""; \n' \
        'for{i in 1..9, j in 1..9, k in 1..9} {\n' \
        '    if ( x[i,j,k] == 1 ) then {\n'\
        '     printf \"%s\", k;\n' \
        '  }\n' \
        '  printf "";\n' \
        '}\n' \

        i_comments = ""

        job_xml = job_template % (i_category, i_solver, i_email, model, data, commands, i_comments)
        return job_xml

if __name__ == '__main__':
  if len(sys.argv) == 3 and len(sys.argv[1]) == 81:
    job_xml = prepare_NEOS_job("lp", "CPLEX", sys.argv[2], sys.argv[1])
    print(solve_with_NEOS(job_xml))
  else:
    print ('Usage: python sudoku.py puzzle')
    print ('  where puzzle is an 81 character string representing the puzzle read left-to-right, top-to-bottom, and 0 is a blank')
