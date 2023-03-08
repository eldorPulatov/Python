FROM python
LABEL maintainer="lorenz.vanthillo@gmail.com"
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["python"]
CMD ["index.py"]