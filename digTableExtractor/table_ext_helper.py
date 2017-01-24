from bs4 import BeautifulSoup
import re

def is_data_cell(cell):
	if(cell.table):
		return False
	return True

def is_data_row(row):
	if(row.table):
		return False
	cell = row.findAll('td', recursive=False)
	if cell is None:
		cell = row.findAll('th', recursive=False)
	for td in cell:
		if(is_data_cell(td) == False):
			return False
	return True

def get_data_rows(table):
	data_rows = []
	rows = table.findAll('tr', recursive=False)
	for tr in rows:
		if(is_data_row(tr)):
			data_rows.append(str(tr))
	return data_rows

def is_data_table(table, k):
	rows = get_data_rows(table)
	if(len(rows) > k):
		return rows
	else:
		return False

# def table_extract(html_doc):
# 	soup = BeautifulSoup(html_doc, 'html.parser')
	
# 	if(soup.table == None):
# 		return None
# 	else:
# 		dict = {}
# 		dict["tables"] = []
# 		tables = soup.findAll('table')
# 		for table in tables:
# 			data_table = {}
# 			rows = is_data_table(table, 2)
# 			if(rows != False):
# 				data_table["rows"] = rows
# 				dict["tables"].append(data_table)
# 		return dict



# Computes mean of a list of numbers
def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

# Check if a string contains a digit
_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))


def table_extract(html_doc):
	soup = BeautifulSoup(html_doc, 'html.parser')
	
	if(soup.table == None):
		return None
	else:
		dict = {}
		dict["tables"] = []
		tables = soup.findAll('table')
		for table in tables:
			tdcount = 0
			max_tdcount = 0
			img_count = 0
			href_count = 0
			inp_count = 0
			sel_count = 0
			colspan_count = 0
			colon_count = 0
			len_row = 0
			table_data = ""
			data_table = {}
			row_list = []
			rows = is_data_table(table, 2)
			if(rows != False):
				features = {}
				for row in rows:
					row_dict = {}
					soup_row = BeautifulSoup(row, 'html.parser')
					row_data = ''.join(soup_row.stripped_strings)
					row_data = row_data.replace("\\t", "").replace("\\r", "").replace("\\n", "")
					if row_data != '':
						row_tdcount = len(soup_row.findAll('td')) + len(soup_row.findAll('th'))
						if(row_tdcount > max_tdcount):
							max_tdcount = row_tdcount
						tdcount += row_tdcount
						img_count += len(soup_row.findAll('img'))
						href_count += len(soup_row.findAll('a'))
						inp_count += len(soup_row.findAll('input'))
						sel_count += len(soup_row.findAll('select'))
						colspan_count += row_data.count("colspan")
						colon_count += row_data.count(":")
						len_row += 1
						table_data += row
						# row_dict["row"] = str(row)
						cell_list = []
						for td in soup_row.findAll('td'):
							cell_dict = {}
							cell_dict["cell"] = str(td)
							cell_dict["text"] = [{"result": {"value": ''.join(td.stripped_strings)}}]
							cell_list.append(cell_dict)
						row_dict["cells"] = cell_list
						row_list.append(row_dict)

				if len_row == 0:
					tdcount = 1
				features["no_of_rows"] = len_row
				features["no_of_cells"] = tdcount
				features["max_cols_in_a_row"] = max_tdcount
				features["ratio_of_img_tags_to_cells"] = img_count*1.0/tdcount
				features["ratio_of_href_tags_to_cells"] = href_count*1.0/tdcount
				features["ratio_of_input_tags_to_cells"] = inp_count*1.0/tdcount
				features["ratio_of_select_tags_to_cells"] = sel_count*1.0/tdcount
				features["ratio_of_colspan_tags_to_cells"] = colspan_count*1.0/tdcount
				features["ratio_of_colons_to_cells"] = colon_count*1.0/tdcount
				if(colspan_count == 0.0 and len_row != 0 and (tdcount/(len_row * 1.0)) == max_tdcount):
					col_data = {}
					for i in range(max_tdcount):
						col_data['c_{0}'.format(i)] = []
					soup_col = BeautifulSoup(table_data, 'html.parser')
					for row in soup_col.findAll('tr'):
						h_index = 0
						h_bool = True
						for col in row.findAll('th'):
							col_content = ''.join(col.stripped_strings)
							h_bool = False
							if col_content is None:
								continue
							else:
								col_data['c_{0}'.format(h_index)].append(col_content)
							h_index += 1
						d_index = 0
						if(h_index == 0 and h_bool == False):
							d_index = 1
						for col in row.findAll('td'):
							col_content = ''.join(col.stripped_strings)
							if col_content is None:
								d_index += 1
								continue
							else:
								col_data['c_{0}'.format(d_index)].append(col_content)
							d_index += 1

					for key, value in col_data.iteritems():
						whole_col = ''.join(value)
						features["column_" + str(key) + "_average_len"] = float("%.2f" % mean([len(x) for x in value]))
						features["column_" + str(key) + "_contains_num"] = contains_digits(whole_col)
						features["column_" + str(key) + "_is_only_num"] = whole_col.isdigit()
						features["column_" + str(key) + "_is_empty"] = (whole_col == '')
				data_table["features"] = features
				data_table["rows"] = row_list
				dict["tables"].append(data_table)
		return dict


def table_decompose(html_doc):
	soup = BeautifulSoup(html_doc, 'html.parser')
	tables = soup.findAll('table')
	for table in tables:
		rows = is_data_table(table, 2)
		if(rows != False):
			table.decompose()
	
	return soup