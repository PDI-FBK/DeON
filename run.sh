rm -r ./build
python setup.py clean build install
./bin/deon-dataset-create --tmp ./tmp_dataset --split 90,10  --balanced_split --ignore_from ./tmp_dataset/random\ selected/3/all.tsv ./tmp_dataset/random\ selected/1/randomselector_all.tsv

cd tmp_dataset
cp train.tsv ./multiple_train_files/
cp test.tsv ./multiple_train_files/

cd ./multiple_train_files
split -l 10000 train.tsv train.x
rm train.tsv
for file in train.*; do
    mv "$file" "${file%}.tsv";
done

cd ../../
./bin/deon-dataset-create --tmp ./tmp_dataset/multiple_train_files --rio ./tmp_dataset/multiple_train_files/*.tsv
