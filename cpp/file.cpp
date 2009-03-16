#include <QTextStream>
#include <QFile>

int main()
{
	QFile data("myfile");

	if (data.open(QFile::WriteOnly)) {
		QTextStream out(&data);
		out << "You make me want to be a better man." << endl;
	}
}
