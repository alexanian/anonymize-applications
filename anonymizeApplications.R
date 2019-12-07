anonymizeApplications <- function(applications_csv = "./anonymizeApplications.testData.csv",
                                  name_cols = c(2,12), grouping_cols = c(13:16),
                                  info_cols = c(4:5, 8:10),
                                  subheading_cols = c(3,5,4),
                                  question_cols = c(6, 11, 17:41)) {
# Script to take CSV input and format each row as an HTML document. Originally
# written for anonymizing applications for the Waterloo iGEM Team that were
# received the spreadsheet output of a Google Form. The inputs are:
#
# applications_csv: CSV file containing rows to be converted into HTML docs
# name_cols:        Entries in these column #s will be matched with row #s &
#                   output to a doc called names_key.csv with the row #s. You 
#                   may need to remove multiple columns for anonymization, e.g.
#                   e-mail addresses as well as names
# grouping_cols:    Columns that should be used to identify the applicant by
#                   being added to the title. This script has a specific logic
#                   related to the Waterloo iGEM Subteams
# info_cols:        Not question-and-answer, should be put in rows beneath the 
#                   applicant info and subheading
# subheading_cols:  Pasted as a subheading below each applicant number in their
#                   HTML doc
# question_cols:    The column title is assumed to be a question, which will be
#                   bolded and followed by the row's value for the column.
#
# Default input values should produce decent results with the sample file
# anonymizeApplications.testData.csv
#
# Outputs one HTML document per (non-header) row of applications_csv named
# Appicant_<Row#>_<GroupingColsInfo>.html
  

# Require check.names=FALSE in order to use column names as question strings-
# otherwise will have punctuation replaced by periods
all_applications <- read.csv(applications_csv, header=TRUE,
                             stringsAsFactors = FALSE, check.names=FALSE)
num_applicants <- nrow(all_applications)

# Assign applicant #s based on row #s to refer to applicants in place of names
name_key <- cbind(1:num_applicants, all_applications[,name_cols])
write.table(name_key, "./names_key.csv", append=FALSE, sep=",")

# Each applicant should be written to their own file
for(row in 1:num_applicants) { 
  applicant_number <- row
  application <- all_applications[row,]
  
  # Output filename defined using team-specific logic based on grouping_cols
  outfile = paste("./Applicant_", applicant_number, sep="")
  if(application[grouping_cols[1]] == "Yes") { # Math
    outfile = paste(outfile, "MAT", sep="_")
  } 
  if(application[grouping_cols[2]] == "Yes") { # Lab & Design
    outfile = paste(outfile, "LAB", sep="_")
  }
  if(application[grouping_cols[3]] == "Yes") { # Policy & Practices
    outfile = paste(outfile, "PNP", sep="_")
  }
  if(application[grouping_cols[4]] == "Yes") { # Business
    outfile = paste(outfile, "BUS", sep="_")
  }
  outfile = paste(outfile, ".html", sep="")

  # Add HTML header with a tiny amount of style and a heading + subheading
  html_out <- paste("<html><head><style type=\"text/css\">
                     div.wrapper {
                     width: 700px;
                     padding: 20px 50px;
                     background: #d6dcde;
                     font-family: Helvetica, Sans-serif;
                     }
                     </style></head>
                     <body>
                     <div class=\"wrapper\">
                     <h1>Applicant", applicant_number,"</h1>
                     <h2>", paste(application[subheading_cols], sep="",
                                  collapse=" "),
                     "</h2>\n",
                     sep=" ")

  # Add non-question information (e.g. faculty) below heading
  # Sort of hacking nested paste functions so that each colname-rowresponse
  # pair is wrapped approrpiately
  html_out <- paste(html_out, paste("<b>", colnames(application[info_cols]),
                                    "</b>: ", application[info_cols],
                                    "<br />", sep="", collapse="\n"),
                    "\n<p>&nbsp;</p>\n")

  # Keep columns with answered questions
  application <- application[question_cols]
  application <- application[which((!is.na(application))& 
                                             (application != ""))] # and that have answers
  
  # Print questions
  html_out <- paste(html_out, paste("<p><b>", colnames(application),
                                  "</b></p>\n<p>", application, "</p>\n",
                                  sep="", collapse="\n"),
                    "</div>\n</body>\n</html>")
  write(html_out, outfile, append=FALSE)
  
}
}
