import io
import json

import xlsxwriter
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools import html_escape


class WarrantyExcelReportController(http.Controller):
    @http.route('/product_warranty/excel_report/<model(w"warranty.wizard"):report_id>',
                type='http', auth='user', csrf=False)
    def get_report_xlsx(self, report_id=None):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition',
                 content_disposition('Warranty Report' + '.xlsx'))
            ]
        )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        report_lines = report_id.get_report_lines()
        sql_data = report_lines.get('sql_data')
        head = workbook.add_format({'font_name': 'Arial',
                                    'font_size': 16, 'bold': True,
                                    'align': 'center'})
        sheet = workbook.add_worksheet("warranty")
        sheet.merge_range('A1:F1', 'PRODUCT WARRANTY', head)
        sheet.set_column(1, 5, 30)
        text = workbook.add_format({'font_name': 'Arial',
                                    'font_size': 14, 'bold': True,
                                    'align': 'center'})
        value = workbook.add_format({'font_name': 'Arial',
                                     'font_size': 14, 'align': 'center'})

        sheet.write(7, 0, 'No.', text)
        sheet.write(7, 1, 'Reference no', text)
        sheet.write(7, 2, 'Invoice', text)
        sheet.write(7, 3, 'Request Date', text)

        val = 3

        if report_lines.get('product_ids'):
            sheet.write(3, 1, 'Products:' + report_lines.get('product_ids'),
                        text)
        else:
            val += 1
            sheet.write(7, val, 'Product', text)

        if report_lines.get('customer_id'):
            sheet.write(4, 1, 'Customer:' + report_lines.get('customer_id'),
                        text)
        else:
            val += 1
            sheet.write(7, val, 'Customer', text)

        if report_lines.get('start_date'):
            sheet.write(5, 1,
                        'From Date:' + str(report_lines.get('start_date')),
                        text)

        if report_lines.get('end_date'):
            sheet.write(5, 2,
                        'To Date:' + str(report_lines.get('end_date')),
                        text)

        row = 8
        number = 1

        for line in sql_data:
            sheet.set_row(row, 20)
            sheet.write(row, 0, number, value)
            sheet.write(row, 1, line['reference_no'], value)
            sheet.write(row, 2, line['invoice_id'], value)
            sheet.write(row, 3, str(line['request_date']), value)

            col = 3

            if report_lines.get('product_ids') == False:
                col += 1
                sheet.write(row, col, line['product'], value)

            if report_lines.get('customer_id') == False:
                col += 1
                sheet.write(row, col, line['customer'], value)

            row += 1
            number += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response


class XLSXReportController(http.Controller):
    @http.route('/xlsx_reports', type='http',
                auth='user', methods=['POST'], csrf=False)
    def get_report_xlsx(self, model, options,
                        output_format, report_name, **kw):
        uid = request.session.uid
        report_obj = request.env[model].with_user(uid)
        options = json.loads(options)
        token = 'dummy-because-api-expects-one'
        try:
            if output_format == 'xlsx':
                response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition',
                         content_disposition(report_name + '.xlsx'))
                    ]
                )
                data = report_obj.get_xlsx_report(options, response)
            response.set_cookie('fileToken', token)

            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            sql_data = data.get('sql_data')
            head = workbook.add_format({'font_name': 'Arial',
                                        'font_size': 16, 'bold': True, 'align': 'center'})
            sheet = workbook.add_worksheet("warranty")
            sheet.merge_range('A1:F1', 'PRODUCT WARRANTY', head)
            sheet.set_column(1, 5, 30)
            text = workbook.add_format({'font_name': 'Arial',
                                        'font_size': 14, 'bold': True, 'align': 'center'})
            value = workbook.add_format({'font_name': 'Arial',
                                         'font_size': 14, 'align': 'center'})

            sheet.write(7, 0, 'No.', text)
            sheet.write(7, 1, 'Reference no', text)
            sheet.write(7, 2, 'Invoice', text)
            sheet.write(7, 3, 'Request Date', text)

            val = 3

            if data.get('product_ids'):
                sheet.write(3, 1, 'Products:' +
                            data.get('product_ids'), text)
            else:
                val += 1
                sheet.write(7, val, 'Product', text)

            if data.get('customer_id'):
                sheet.write(4, 1, 'Customer:' +
                            data.get('customer_id'), text)
            else:
                val += 1
                sheet.write(7, val, 'Customer', text)

            if data.get('start_date'):
                sheet.write(5, 1, 'From Date:' +
                            str(data.get('start_date')), text)

            if data.get('end_date'):
                sheet.write(5, 2, 'To Date:' + str(data.get('end_date')), text)

            row = 8
            number = 1

            for line in sql_data:
                sheet.set_row(row, 20)
                sheet.write(row, 0, number, value)
                sheet.write(row, 1, line['reference_no'], value)
                sheet.write(row, 2, line['invoice_id'], value)
                sheet.write(row, 3, str(line['request_date']), value)

                col = 3

                if data.get('product_ids') == False:
                    col += 1
                    sheet.write(row, col, line['product'], value)
                #
                if data.get('customer_id') == False:
                    col += 1
                    sheet.write(row, col, line['customer'], value)

                row += 1
                number += 1
            workbook.close()
            output.seek(0)
            response.stream.write(output.read())
            output.close()

            return response
        except Exception as e:
            se = http.serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se}

        return request.make_response(html_escape(json.dumps(error)))
